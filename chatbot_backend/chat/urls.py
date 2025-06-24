from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_message, name='chat_message'),
    path('conversations/', views.get_conversations, name='get_conversations'),
    path('conversations/<int:conversation_id>/', views.get_conversation, name='get_conversation'),
]