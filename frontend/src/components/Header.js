import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import { LogOut, User } from 'lucide-react';

function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="header">
      <div className="container">
        <nav className="nav">
          <a href="/" className="nav-brand">
            PLA - Athena
          </a>
          
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">
              Welcome, {user?.email}
            </span>
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => {/* TODO: Profile modal */}}
                className="btn btn-outline btn-sm"
              >
                <User size={16} />
                Profile
              </button>
              
              <button
                onClick={logout}
                className="btn btn-outline btn-sm"
              >
                <LogOut size={16} />
                Logout
              </button>
            </div>
          </div>
        </nav>
      </div>
    </header>
  );
}

export default Header; 