import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api.js';

const ChatView = () => {
  const { id } = useParams();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationTitle, setConversationTitle] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    if (id !== 'new') {
      fetchConversation();
    } else {
      setConversationTitle('New Chat');
    }
  }, [id]);

  const fetchConversation = async () => {
    try {
      const response = await api.get(`/api/conversations/${id}/`);
      console.log('Fetched conversation:', response.data);
      
      // Parse the conversation structure to extract messages
      if (response.data.conversation) {
        setMessages(response.data.conversation.messages || []);
        setConversationTitle(response.data.conversation.title);
      } else {
        // Fallback for direct message array
        setMessages(response.data.messages || []);
        setConversationTitle(response.data.title || 'Chat');
      }
    } catch (error) {
      console.error('Failed to fetch conversation:', error);
      navigate('/dashboard');
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    setLoading(true);
    const messageText = newMessage;
    setNewMessage('');

    try {
      const payload = {
        message: messageText,
        ...(id !== 'new' && { conversation_id: parseInt(id) })
      };

      const response = await api.post('/api/chat/', payload);
      
      if (id === 'new') {
        // Navigate to the new conversation
        navigate(`/chat/${response.data.conversation_id}`);
      } else {
        // Add messages to current conversation
        setMessages(prev => [...prev, response.data.user_message, response.data.ai_message]);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setNewMessage(messageText); // Restore message on error
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-screen flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-semibold text-gray-900">{conversationTitle}</h1>
          <button
            onClick={() => navigate('/dashboard')}
            className="text-gray-500 hover:text-gray-700 px-3 py-1 rounded-md text-sm"
          >
            Back to Dashboard
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Start a conversation by sending a message below.</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.is_user ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                  message.is_user
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                <p className="text-sm">{message.content}</p>
                <p className="text-xs mt-1 opacity-70">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="max-w-xs lg:max-w-md px-4 py-2 rounded-lg bg-gray-200">
              <div className="flex items-center space-x-2">
                <div className="animate-bounce w-2 h-2 bg-gray-500 rounded-full"></div>
                <div className="animate-bounce w-2 h-2 bg-gray-500 rounded-full" style={{animationDelay: '0.1s'}}></div>
                <div className="animate-bounce w-2 h-2 bg-gray-500 rounded-full" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Message Input */}
      <div className="bg-white border-t border-gray-200 p-6">
        <form onSubmit={sendMessage} className="flex space-x-4">
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !newMessage.trim()}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-md font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatView;