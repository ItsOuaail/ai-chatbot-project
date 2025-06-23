from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('chat/', views.chat_message, name='chat_message'),
    path('conversations/', views.get_conversations, name='get_conversations'),
    path('conversations/<int:conversation_id>/', views.get_conversation, name='get_conversation'),
    path('admin/', admin.site.urls),
    path('api/', include('chat.urls')),
]