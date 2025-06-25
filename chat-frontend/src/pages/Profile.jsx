import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const Profile = () => {
  const { user } = useAuth();
  
  if (!user) return null;
  
  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white shadow-xl rounded-xl overflow-hidden">
          {/* Profile Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-500 px-6 py-8 text-white">
            <div className="flex items-center space-x-4">
              <div className="h-16 w-16 rounded-full bg-white/20 flex items-center justify-center text-2xl font-bold">
                {user.user.first_name?.charAt(0) || user.user.username.charAt(0)}
              </div>
              <div>
                <h1 className="text-2xl font-bold">
                  {user.user.first_name || user.user.username}'s Profile
                </h1>
                <p className="text-blue-100">
                  Member since {new Date(user.user.date_joined).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>

          {/* Profile Details */}
          <div className="p-6 sm:p-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Username */}
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-500">
                  Username
                </label>
                <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <p className="text-gray-900 font-medium">
                    {user.user.username}
                  </p>
                </div>
              </div>

              {/* Email */}
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-500">
                  Email
                </label>
                <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <p className="text-gray-900 font-medium">
                    {user.user.email}
                  </p>
                </div>
              </div>

              {/* First Name */}
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-500">
                  First Name
                </label>
                <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <p className="text-gray-900 font-medium">
                    {user.user.first_name || 'Not provided'}
                  </p>
                </div>
              </div>

              {/* Last Name */}
              <div className="space-y-1">
                <label className="block text-sm font-medium text-gray-500">
                  Last Name
                </label>
                <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <p className="text-gray-900 font-medium">
                    {user.user.last_name || 'Not provided'}
                  </p>
                </div>
              </div>

              {/* Additional Fields */}
              <div className="md:col-span-2 space-y-1">
                <label className="block text-sm font-medium text-gray-500">
                  Account Status
                </label>
                <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="flex items-center">
                    <span className="h-2 w-2 rounded-full bg-green-500 mr-2"></span>
                    <p className="text-gray-900 font-medium">Active</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Edit Button */}
            <div className="mt-8 flex justify-end">
              <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200">
                Edit Profile
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;