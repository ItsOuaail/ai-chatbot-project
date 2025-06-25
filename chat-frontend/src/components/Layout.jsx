import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.jsx';

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {user && (
        <header className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              {/* Left side navigation */}
              <div className="flex items-center space-x-8">
                <Link 
                  to="/dashboard" 
                  className="flex items-center space-x-2"
                >
                  <svg className="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                  <span className="text-xl font-semibold text-gray-900">ChatAI</span>
                </Link>
                <nav className="hidden md:flex space-x-4">
                  <Link 
                    to="/dashboard" 
                    className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 flex items-center"
                  >
                    <svg className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                    </svg>
                    Dashboard
                  </Link>
                  <Link 
                    to="/profile" 
                    className="text-gray-500 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 flex items-center"
                  >
                    <svg className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    Profile
                  </Link>
                </nav>
              </div>

              {/* Right side user controls */}
              <div  className="flex items-center space-x-4">
                
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 text-gray-500 hover:text-gray-700 transition-colors duration-200"
                  title="Logout"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                  <span className="hidden md:inline text-sm font-medium">Logout</span>
                </button>
              </div>
            </div>
          </div>
        </header>
      )}
      <main className="flex-1">
        {children}
      </main>
      
      {/* Footer */}
      {user && (
        <footer className="bg-white border-t mt-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-sm text-gray-500">
                © {new Date().getFullYear()} ChatAI. All rights reserved.
              </p>
              <div className="flex space-x-6 mt-4 md:mt-0">
                <a href="#" className="text-gray-400 hover:text-gray-500">
                  <span className="sr-only">Privacy</span>
                  <span className="text-sm">Privacy Policy</span>
                </a>
                <a href="#" className="text-gray-400 hover:text-gray-500">
                  <span className="sr-only">Terms</span>
                  <span className="text-sm">Terms of Service</span>
                </a>
              </div>
            </div>
          </div>
        </footer>
      )}
    </div>
  );
};

export default Layout;