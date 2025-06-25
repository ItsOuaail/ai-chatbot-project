import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api.js';

const ChatView = () => {
  const { id } = useParams();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [conversationTitle, setConversationTitle] = useState('');
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const navigate = useNavigate();

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    if (id !== 'new') {
      fetchConversation();
    } else {
      setConversationTitle('New Chat');
      setMessages([]);
    }
  }, [id]);

  const fetchConversation = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/conversations/${id}/`);
      
      if (response.data.conversation) {
        setMessages(response.data.conversation.messages || []);
        setConversationTitle(response.data.conversation.title);
      } else {
        setMessages(response.data.messages || []);
        setConversationTitle(response.data.title || 'Chat');
      }
    } catch (error) {
      console.error('Failed to fetch conversation:', error);
      navigate('/dashboard');
    } finally {
      setLoading(false);
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
        navigate(`/chat/${response.data.conversation_id}`);
      } else {
        setMessages(prev => [...prev, response.data.user_message, response.data.ai_message]);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setNewMessage(messageText);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between sticky top-0 z-10">
        <button
          onClick={() => navigate('/dashboard')}
          className="flex items-center text-gray-600 hover:text-gray-900"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back
        </button>
        <h1 className="text-lg font-medium text-gray-900">{conversationTitle}</h1>
        <div className="w-10"></div> {/* Spacer for balance */}
      </div>

      {/* Messages Container - Now scrolls independently */}
      <div 
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto p-6 space-y-4 pb-24" /* Added pb-24 to account for input height */
      >
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500">
            <svg className="w-16 h-16 mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            <p className="text-gray-400">No messages yet</p>
            <p className="text-sm mt-1 text-gray-400">Start the conversation below</p>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.is_user ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] px-4 py-3 rounded-lg ${
                  message.is_user
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-800 shadow-sm border border-gray-100'
                }`}
              >
                <p className="whitespace-pre-wrap">{message.content}</p>
                <p className={`text-xs mt-1 ${
                  message.is_user ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white shadow-sm border border-gray-100 px-4 py-3 rounded-lg">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Fixed Input Area at Bottom */}
      <div className="bg-white border-t border-gray-200 p-4 fixed bottom-0 left-0 right-0">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={sendMessage} className="flex items-center space-x-3">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type a message..."
              className="flex-1 px-4 py-3 bg-gray-50 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white border border-gray-200"
              disabled={loading}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  sendMessage(e);
                }
              }}
            />
            <button
              type="submit"
              disabled={loading || !newMessage.trim()}
              className={`p-3 rounded-full transition-colors ${
                newMessage.trim() 
                  ? 'bg-blue-600 text-white hover:bg-blue-700' 
                  : 'bg-gray-200 text-gray-400'
              }`}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ChatView;