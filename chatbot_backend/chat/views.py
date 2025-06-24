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
    # 1. Validate incoming data
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # 2. Extract validated data
    message_content = serializer.validated_data['message']
    conversation_id = serializer.validated_data.get('conversation_id')
    
    # 3. Conversation handling - pass the authenticated user
    conversation = AIService.get_or_create_conversation(conversation_id, user=request.user)
    
    # 4. Save user message
    user_message = Message.objects.create(
        conversation=conversation,
        content=message_content,
        is_user=True
    )
    
    # 5. Get AI response
    try:
        ai_response = AIService.get_ai_response(
            message_content,
            conversation_id=conversation.id
        )
    except Exception as e:
        logger.error(f"AI Service error: {str(e)}")
        return Response(
            {'error': 'AI service unavailable'}, 
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    # 6. Save AI response
    ai_message = Message.objects.create(
        conversation=conversation,
        content=ai_response,
        is_user=False
    )
    
    # 7. Update conversation timestamp
    conversation.save()  # Triggers auto_now=True on updated_at
    
    # 8. Return response
    return Response({
        'conversation_id': conversation.id,
        'user_message': MessageSerializer(user_message).data,
        'ai_message': MessageSerializer(ai_message).data,
        'conversation_title': conversation.title
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversations(request):
    # 1. Get user's conversations only
    conversations = Conversation.objects.filter(user=request.user) \
                      .prefetch_related('messages') \
                      .order_by('-updated_at')[:10]
    
    # 2. Serialize with message count
    serializer = ConversationSerializer(conversations, many=True)
    
    # 3. Add pagination metadata
    return Response({
        'count': len(serializer.data),
        'results': serializer.data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation(request, conversation_id):
    try:
        # 1. Get user's conversation only
        conversation = Conversation.objects \
            .prefetch_related('messages') \
            .get(id=conversation_id, user=request.user)
            
        # 2. Serialize with nested messages
        serializer = ConversationSerializer(conversation)
        
        return Response(serializer.data)
        
    except Conversation.DoesNotExist:
        return Response(
            {'error': 'Conversation not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )