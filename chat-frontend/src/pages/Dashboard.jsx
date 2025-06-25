import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api.js';

const Dashboard = () => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      const response = await api.get('/api/conversations/');
      setConversations(response.data.results || []);
    } catch (error) {
      console.error('Failed to fetch conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const deleteConversation = async (id) => {
    if (window.confirm('Are you sure you want to delete this conversation?')) {
      try {
        await api.delete(`/api/conversations/${id}/delete/`);
        setConversations(conversations.filter(conv => conv.id !== id));
      } catch (error) {
        console.error('Failed to delete conversation:', error);
      }
    }
  };

  const startNewChat = () => {
    navigate('/chat/new');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Chat Dashboard</h1>
        <button
          onClick={startNewChat}
          className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md font-medium"
        >
          New Chat
        </button>
      </div>

      {conversations.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg mb-4">No conversations yet</p>
          <button
            onClick={startNewChat}
            className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-md font-medium"
          >
            Start Your First Chat
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {conversations.map((conversation) => (
            <div
              key={conversation.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {conversation.title}
                  </h3>
                  <p className="text-sm text-gray-500 mb-2">
                    {conversation.message_count} messages
                  </p>
                  <p className="text-xs text-gray-400">
                    Updated: {new Date(conversation.updated_at).toLocaleDateString()}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => navigate(`/chat/${conversation.id}`)}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium"
                  >
                    Open
                  </button>
                  <button
                    onClick={() => deleteConversation(conversation.id)}
                    className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-md text-sm font-medium"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;