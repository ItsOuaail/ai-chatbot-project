import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, ChatRequestSerializer, MessageSerializer
from .services import AIService

# Add logger
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_message(request):
    """
    Enhanced chat message endpoint with:
    - Better error handling
    - Conversation context
    - Automatic title generation
    """
    # 1. Validate incoming data
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning(f"Invalid chat request from user {request.user.username}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 2. Extract validated data
    message_content = serializer.validated_data['message']
    conversation_id = serializer.validated_data.get('conversation_id')
    
    logger.info(f"Processing chat message from user {request.user.username}, conversation_id: {conversation_id}")
    
    try:
        # 3. Conversation handling - pass the authenticated user
        conversation = AIService.get_or_create_conversation(conversation_id, user=request.user)
        
        # 4. Save user message
        user_message = Message.objects.create(
            conversation=conversation,
            content=message_content,
            is_user=True
        )
        
        logger.info(f"Saved user message {user_message.id} to conversation {conversation.id}")
        
        # 5. Get AI response with conversation context
        try:
            ai_response = AIService.get_ai_response(
                message_content,
                conversation_id=conversation.id,
                user=request.user
            )
        except Exception as e:
            logger.error(f"AI Service error for user {request.user.username}: {str(e)}")
            ai_response = "I'm sorry, I'm having trouble processing your request right now. Please try again later."
        
        # 6. Save AI response
        ai_message = Message.objects.create(
            conversation=conversation,
            content=ai_response,
            is_user=False
        )
        
        logger.info(f"Saved AI message {ai_message.id} to conversation {conversation.id}")
        
        # 7. Update conversation title if it's still "New Chat" and we have messages
        if conversation.title == "New Chat" and conversation.messages.count() >= 2:
            try:
                new_title = AIService.get_conversation_summary(conversation.id, request.user)
                conversation.title = new_title
                logger.info(f"Updated conversation {conversation.id} title to: {new_title}")
            except Exception as e:
                logger.warning(f"Failed to generate conversation title: {str(e)}")
        
        # 8. Update conversation timestamp
        conversation.save()  # Triggers auto_now=True on updated_at
        
        # 9. Return comprehensive response
        return Response({
            'conversation_id': conversation.id,
            'user_message': MessageSerializer(user_message).data,
            'ai_message': MessageSerializer(ai_message).data,
            'conversation_title': conversation.title,
            'message_count': conversation.messages.count(),
            'success': True
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Unexpected error in chat_message for user {request.user.username}: {str(e)}")
        return Response({
            'error': 'An unexpected error occurred while processing your message',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversations(request):
    """
    Enhanced conversations list endpoint with:
    - Pagination support
    - Search functionality
    - Better performance with prefetch_related
    """
    try:
        # Get query parameters
        search = request.GET.get('search', '').strip()
        limit = min(int(request.GET.get('limit', 20)), 50)  # Max 50 conversations
        offset = int(request.GET.get('offset', 0))
        
        # Base queryset - user's conversations only
        queryset = Conversation.objects.filter(user=request.user) \
                      .prefetch_related('messages') \
                      .order_by('-updated_at')
        
        # Apply search filter if provided
        if search:
            queryset = queryset.filter(title__icontains=search)
            logger.info(f"User {request.user.username} searching conversations for: {search}")
        
        # Get total count before pagination
        total_count = queryset.count()
        
        # Apply pagination
        conversations = queryset[offset:offset + limit]
        
        # Serialize the data
        serializer = ConversationSerializer(conversations, many=True)
        
        logger.info(f"Returning {len(serializer.data)} conversations for user {request.user.username}")
        
        # Return paginated response
        return Response({
            'count': total_count,
            'next': offset + limit if offset + limit < total_count else None,
            'previous': offset - limit if offset >= limit else None,
            'results': serializer.data,
            'success': True
        }, status=status.HTTP_200_OK)
        
    except ValueError as e:
        logger.warning(f"Invalid pagination parameters from user {request.user.username}: {str(e)}")
        return Response({
            'error': 'Invalid pagination parameters',
            'success': False
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error fetching conversations for user {request.user.username}: {str(e)}")
        return Response({
            'error': 'Failed to fetch conversations',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation(request, conversation_id):
    """
    Enhanced single conversation endpoint with:
    - Message pagination
    - Better error handling
    - Performance optimizations
    """
    try:
        # Get query parameters for message pagination
        message_limit = min(int(request.GET.get('message_limit', 50)), 100)  # Max 100 messages
        message_offset = int(request.GET.get('message_offset', 0))
        
        # Get user's conversation only
        conversation = Conversation.objects.get(
            id=conversation_id, 
            user=request.user
        )
        
        # Get messages with pagination
        messages = conversation.messages.order_by('timestamp')[message_offset:message_offset + message_limit]
        total_messages = conversation.messages.count()
        
        # Create response data
        conversation_data = ConversationSerializer(conversation).data
        
        # Override messages with paginated results
        conversation_data['messages'] = MessageSerializer(messages, many=True).data
        conversation_data['total_messages'] = total_messages
        conversation_data['messages_next'] = message_offset + message_limit if message_offset + message_limit < total_messages else None
        conversation_data['messages_previous'] = message_offset - message_limit if message_offset >= message_limit else None
        
        logger.info(f"User {request.user.username} accessed conversation {conversation_id}")
        
        return Response({
            'conversation': conversation_data,
            'success': True
        }, status=status.HTTP_200_OK)
        
    except Conversation.DoesNotExist:
        logger.warning(f"User {request.user.username} tried to access non-existent conversation {conversation_id}")
        return Response({
            'error': 'Conversation not found',
            'success': False
        }, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        logger.warning(f"Invalid parameters for conversation {conversation_id} from user {request.user.username}: {str(e)}")
        return Response({
            'error': 'Invalid parameters',
            'success': False
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error fetching conversation {conversation_id} for user {request.user.username}: {str(e)}")
        return Response({
            'error': 'Failed to fetch conversation',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_conversation(request, conversation_id):
    """Delete a specific conversation"""
    try:
        conversation = Conversation.objects.get(
            id=conversation_id, 
            user=request.user
        )
        
        conversation_title = conversation.title
        conversation.delete()
        
        logger.info(f"User {request.user.username} deleted conversation {conversation_id}: {conversation_title}")
        
        return Response({
            'message': f'Conversation "{conversation_title}" deleted successfully',
            'success': True
        }, status=status.HTTP_200_OK)
        
    except Conversation.DoesNotExist:
        logger.warning(f"User {request.user.username} tried to delete non-existent conversation {conversation_id}")
        return Response({
            'error': 'Conversation not found',
            'success': False
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error deleting conversation {conversation_id} for user {request.user.username}: {str(e)}")
        return Response({
            'error': 'Failed to delete conversation',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_conversation_title(request, conversation_id):
    """Update conversation title"""
    try:
        conversation = Conversation.objects.get(
            id=conversation_id, 
            user=request.user
        )
        
        new_title = request.data.get('title', '').strip()
        if not new_title:
            return Response({
                'error': 'Title is required',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_title) > 200:
            return Response({
                'error': 'Title too long (max 200 characters)',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        old_title = conversation.title
        conversation.title = new_title
        conversation.save()
        
        logger.info(f"User {request.user.username} updated conversation {conversation_id} title from '{old_title}' to '{new_title}'")
        
        return Response({
            'message': 'Conversation title updated successfully',
            'title': new_title,
            'success': True
        }, status=status.HTTP_200_OK)
        
    except Conversation.DoesNotExist:
        logger.warning(f"User {request.user.username} tried to update non-existent conversation {conversation_id}")
        return Response({
            'error': 'Conversation not found',
            'success': False
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error updating conversation title {conversation_id} for user {request.user.username}: {str(e)}")
        return Response({
            'error': 'Failed to update conversation title',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)