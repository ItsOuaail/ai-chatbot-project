import requests
from django.conf import settings
from django.core.cache import cache
from .models import Conversation
import logging

logger = logging.getLogger(__name__)

class AIService:
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
    def get_ai_response(message, conversation_id=None):
        """
        Main method to get AI response - switches between demo and Gemini based on settings
        conversation_id parameter added for compatibility with views but not used in current implementation
        """
        demo_mode = getattr(settings, 'DEMO_MODE', False)
        logger.info(f"AI Service - DEMO_MODE: {demo_mode}, Message: {message}")
        
        if demo_mode:
            logger.info("Using demo response")
            return AIService._get_demo_response(message)
        
        logger.info("Using Gemini API")
        return AIService._get_gemini_response(message)

    @staticmethod
    def _get_demo_response(message):
        """Fallback demo responses for testing"""
        responses = {
            "hello": "Hello! How can I help you today?",
            "how are you": "I'm doing great! Thanks for asking.",
            "what is your name": "I'm your AI assistant powered by Gemini!",
            "bye": "Goodbye! Have a great day!",
        }
        message_lower = message.lower()
        return next(
            (resp for phrase, resp in responses.items() if phrase in message_lower),
            f"I understand you said: '{message}'. Could you elaborate?"
        )

    @staticmethod
    def _get_gemini_response(message):
        """
        Actual Gemini API implementation with:
        - Caching
        - Error handling
        - Timeouts
        """
        cache_key = f"gemini_res_{hash(message)}"
        if cached := cache.get(cache_key):
            return cached

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        params = {'key': settings.GEMINI_API_KEY}
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            "contents": [{
                "parts": [{"text": message}]
            }],
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_DANGEROUS",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ],
            "generationConfig": {
                "temperature": 0.9,
                "topP": 1,
                "maxOutputTokens": 2048
            }
        }

        try:
            response = requests.post(
                url,
                params=params,
                json=payload,
                headers=headers,
                timeout=10  # 10-second timeout
            )
            response.raise_for_status()
            
            data = response.json()
            if not data.get('candidates'):
                raise ValueError("No candidates in response")
                
            ai_text = data['candidates'][0]['content']['parts'][0]['text']
            cache.set(cache_key, ai_text, timeout=3600)  # Cache for 1 hour
            return ai_text

        except requests.Timeout:
            logger.warning("Gemini API timeout")
            return "The AI is taking longer than usual to respond. Please try again."
            
        except requests.RequestException as e:
            logger.error(f"Gemini API error: {str(e)}")
            return "I'm having trouble connecting to the AI service right now."
            
        except (KeyError, ValueError) as e:
            logger.error(f"Response parsing error: {str(e)}")
            return "I received an unexpected response format from the AI service."