import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Calendar, 
  BookOpen, 
  MessageCircle, 
  Upload,
  TrendingUp,
  Clock,
  Target
} from 'lucide-react';
import api from '../services/api';

function Dashboard() {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/progress/dashboard');
      setDashboardData(response.dashboard);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading"></div>
      </div>
    );
  }

  const stats = [
    {
      title: 'Plan Adherence',
      value: `${dashboardData?.plan_adherence || 0}%`,
      icon: Target,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      title: 'Topics Mastered',
      value: dashboardData?.topics_mastered || 0,
      icon: BookOpen,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      title: 'Time Spent',
      value: `${Math.round((dashboardData?.time_spent_minutes || 0) / 60)}h`,
      icon: Clock,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    },
    {
      title: 'Efficiency Score',
      value: `${dashboardData?.efficiency_score || 0}%`,
      icon: TrendingUp,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50'
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's your learning progress.</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div key={index} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-full ${stat.bgColor}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link to="/planner" className="card hover:shadow-lg transition-shadow cursor-pointer">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-50 rounded-full">
              <Calendar className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Create Study Plan</h3>
              <p className="text-sm text-gray-600">Plan your learning journey</p>
            </div>
          </div>
        </Link>

        <Link to="/chat" className="card hover:shadow-lg transition-shadow cursor-pointer">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-50 rounded-full">
              <MessageCircle className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Chat with AI Tutor</h3>
              <p className="text-sm text-gray-600">Get help and explanations</p>
            </div>
          </div>
        </Link>

        <Link to="/uploads" className="card hover:shadow-lg transition-shadow cursor-pointer">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-50 rounded-full">
              <Upload className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Upload Materials</h3>
              <p className="text-sm text-gray-600">Add study documents</p>
            </div>
          </div>
        </Link>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Plans */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Recent Study Plans</h3>
            <Link to="/planner" className="text-sm text-blue-600 hover:text-blue-500">
              View all
            </Link>
          </div>
          <div className="space-y-3">
            {dashboardData?.recent_plans?.length > 0 ? (
              dashboardData.recent_plans.slice(0, 3).map((plan) => (
                <div key={plan.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{plan.title}</p>
                    <p className="text-sm text-gray-600">
                      {plan.topics?.slice(0, 2).join(', ')}
                      {plan.topics?.length > 2 && '...'}
                    </p>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(plan.created_at).toLocaleDateString()}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-4">No study plans yet</p>
            )}
          </div>
        </div>

        {/* Recent Uploads */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Recent Uploads</h3>
            <Link to="/uploads" className="text-sm text-blue-600 hover:text-blue-500">
              View all
            </Link>
          </div>
          <div className="space-y-3">
            {dashboardData?.recent_uploads?.length > 0 ? (
              dashboardData.recent_uploads.slice(0, 3).map((upload) => (
                <div key={upload.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{upload.filename}</p>
                    <p className="text-sm text-gray-600">
                      {upload.file_type.toUpperCase()} • {Math.round(upload.file_size / 1024)}KB
                    </p>
                  </div>
                  <span className={`status-badge status-${upload.status}`}>
                    {upload.status}
                  </span>
                </div>
              ))
            ) : (
              <p className="text-gray-500 text-center py-4">No uploads yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard; 