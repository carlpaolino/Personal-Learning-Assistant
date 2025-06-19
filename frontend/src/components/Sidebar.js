import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  Calendar, 
  MessageCircle, 
  Upload, 
  BarChart3,
  BookOpen
} from 'lucide-react';

function Sidebar() {
  const navItems = [
    { path: '/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/planner', icon: Calendar, label: 'Study Planner' },
    { path: '/chat', icon: MessageCircle, label: 'AI Tutor' },
    { path: '/uploads', icon: Upload, label: 'Uploads' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics' },
  ];

  return (
    <aside className="sidebar">
      <nav className="flex flex-col gap-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`
            }
          >
            <item.icon size={20} />
            {item.label}
          </NavLink>
        ))}
      </nav>
      
      <div className="mt-8 p-4 bg-blue-50 rounded-lg">
        <div className="flex items-center gap-2 mb-2">
          <BookOpen size={16} className="text-blue-600" />
          <span className="text-sm font-medium text-blue-900">Quick Tips</span>
        </div>
        <p className="text-xs text-blue-700">
          Upload study materials to get personalized AI explanations and practice questions.
        </p>
      </div>
    </aside>
  );
}

export default Sidebar; 