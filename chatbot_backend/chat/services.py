import logging
from django.conf import settings
from django.core.cache import cache
from .models import Conversation, Message
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class AIService:
    _client = None
    
    @classmethod
    def get_client(cls):
        """Get or create the Gemini client"""
        if cls._client is None and not settings.DEMO_MODE:
            if not settings.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is required when DEMO_MODE is False")
            cls._client = genai.Client(api_key=settings.GEMINI_API_KEY)
        return cls._client
    
    @staticmethod
    def get_or_create_conversation(conversation_id=None, user=None):
        """Get existing conversation or create a new one for a specific user"""
        if conversation_id and user:
            try:
                # Make sure the conversation belongs to the user
                return Conversation.objects.get(id=conversation_id, user=user)
            except Conversation.DoesNotExist:
                logger.info(f"Conversation {conversation_id} not found for user {user.username}, creating new one")
        
        # Create new conversation for the user
        if user:
            return Conversation.objects.create(title="New Chat", user=user)
        else:
            raise ValueError("User is required to create a conversation")
    
    @staticmethod
    def get_ai_response(message, conversation_id=None, user=None):
        """
        Main method to get AI response - switches between demo and Gemini based on settings
        Now includes conversation history for better context
        """
        demo_mode = getattr(settings, 'DEMO_MODE', False)
        logger.info(f"AI Service - DEMO_MODE: {demo_mode}, Message: {message}")
        
        if demo_mode:
            logger.info("Using demo response")
            return AIService._get_demo_response(message)
        
        logger.info("Using Gemini API with conversation context")
        
        # Get conversation history for context
        conversation_history = []
        if conversation_id and user:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=user)
                # Get last 10 messages for context (excluding the current one)
                recent_messages = conversation.messages.order_by('-timestamp')[:10]
                conversation_history = list(reversed(recent_messages))
            except Conversation.DoesNotExist:
                logger.warning(f"Conversation {conversation_id} not found for context")
        
        return AIService._get_gemini_response(message, conversation_history)

    @staticmethod
    def _get_demo_response(message):
        """Enhanced demo responses for testing"""
        responses = {
            "hello": "Hello! How can I help you today? (Demo Mode)",
            "hi": "Hi there! I'm ready to assist you. (Demo Mode)",
            "how are you": "I'm doing great! Thanks for asking. (Demo Mode)",
            "what is your name": "I'm your AI assistant powered by Gemini! (Demo Mode)",
            "what can you do": "I can help you with various tasks like answering questions, creative writing, coding help, and more! (Demo Mode)",
            "bye": "Goodbye! Have a great day! (Demo Mode)",
            "goodbye": "See you later! Feel free to come back anytime. (Demo Mode)",
            "help": "I'm here to help! You can ask me questions, request explanations, or chat about various topics. (Demo Mode)",
            "test": "This is a test response. Everything is working correctly! (Demo Mode)",
        }
        
        message_lower = message.lower().strip()
        
        # Check for exact matches first
        if message_lower in responses:
            return responses[message_lower]
        
        # Check for partial matches
        for phrase, response in responses.items():
            if phrase in message_lower:
                return response
        
        # Default response with message echo
        return f"Demo Mode: I received your message '{message}'. In real mode, I would provide an intelligent AI response using Gemini!"

    @staticmethod
    def _get_gemini_response(message, conversation_history=None):
        """
        Enhanced Gemini API implementation using the new Google GenAI SDK
        Includes conversation history for better context
        """
        # Create cache key that includes conversation context
        context_hash = hash(str([msg.content for msg in (conversation_history or [])]))
        cache_key = f"gemini_response_{hash(message)}_{context_hash}"
        
        # Check cache first
        if cached_response := cache.get(cache_key):
            logger.info("Returning cached Gemini response")
            return cached_response

        try:
            client = AIService.get_client()
            if not client:
                raise ValueError("Gemini client not available")
            
            # Prepare conversation messages
            messages = []
            
            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg.is_user else "model"
                    # Fixed: Use text parameter instead of positional argument
                    messages.append(types.Content(
                        role=role,
                        parts=[types.Part(text=msg.content)]
                    ))
            
            # Add the current message
            # Fixed: Use text parameter instead of positional argument
            messages.append(types.Content(
                role="user",
                parts=[types.Part(text=message)]
            ))
            
            # Generate response using Gemini 1.5 Flash
            response = client.models.generate_content(
                model='gemini-1.5-flash',
                contents=messages,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    max_output_tokens=1500,
                    top_p=0.8,
                    top_k=40,
                    stop_sequences=None,
                    response_mime_type="text/plain"
                )
            )
            
            # Extract response text
            if response.candidates and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    ai_text = candidate.content.parts[0].text
                    
                    # Cache the response for 1 hour
                    cache.set(cache_key, ai_text, timeout=3600)
                    
                    logger.info("Successfully generated Gemini response")
                    return ai_text
                else:
                    raise ValueError("No content in response candidate")
            else:
                raise ValueError("No candidates in response")

        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            
            # Provide helpful error messages based on error type
            error_message = str(e).lower()
            
            if "api key" in error_message or "authentication" in error_message:
                return "I'm having trouble with my API configuration. Please check that the API key is set correctly."
            elif "quota" in error_message or "rate limit" in error_message:
                return "I'm temporarily unavailable due to high demand. Please try again in a few moments."
            elif "safety" in error_message or "blocked" in error_message:
                return "I can't provide a response to that request due to safety guidelines. Please try rephrasing your question."
            elif "timeout" in error_message:
                return "I'm taking longer than usual to respond. Please try again."
            else:
                return "I'm experiencing some technical difficulties right now. Please try again later."

    @staticmethod
    def get_conversation_summary(conversation_id, user):
        """Generate a summary of the conversation for the title"""
        try:
            conversation = Conversation.objects.get(id=conversation_id, user=user)
            messages = conversation.messages.all()[:5]  # First 5 messages
            
            if not messages:
                return "New Chat"
            
            # Create a summary prompt
            message_text = " ".join([msg.content for msg in messages])
            summary_prompt = f"Create a short title (max 6 words) for this conversation: {message_text[:200]}"
            
            if settings.DEMO_MODE:
                return f"Chat about {message_text.split()[0] if message_text.split() else 'topic'}"
            
            try:
                summary = AIService._get_gemini_response(summary_prompt)
                # Clean up the summary - remove quotes and limit length
                summary = summary.strip().strip('"').strip("'")
                if len(summary) > 50:
                    summary = summary[:47] + "..."
                return summary
            except Exception as e:
                logger.error(f"Error generating conversation summary: {str(e)}")
                return "New Chat"
                
        except Conversation.DoesNotExist:
            return "New Chat"