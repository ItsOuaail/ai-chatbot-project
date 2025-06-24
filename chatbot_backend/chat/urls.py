from django.urls import path
from . import views, auth_views

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', auth_views.register, name='register'),
    path('auth/login/', auth_views.login_user, name='login'),
    path('auth/logout/', auth_views.logout_user, name='logout'),
    path('auth/profile/', auth_views.get_user_profile, name='profile'),
    
    # Chat endpoints
    path('chat/', views.chat_message, name='chat_message'),
    path('conversations/', views.get_conversations, name='get_conversations'),
    path('conversations/<int:conversation_id>/', views.get_conversation, name='get_conversation'),
]