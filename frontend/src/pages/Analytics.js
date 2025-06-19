import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Calendar, Target } from 'lucide-react';
import api from '../services/api';

function Analytics() {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/progress/analytics');
      setAnalyticsData(response.analytics);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
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

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600">Track your learning progress and insights</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-50 rounded-full">
              <BarChart3 className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Total Chat Sessions</p>
              <p className="text-2xl font-bold text-gray-900">
                {analyticsData?.chat_activity?.total_sessions || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-50 rounded-full">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Messages/Session</p>
              <p className="text-2xl font-bold text-gray-900">
                {analyticsData?.chat_activity?.avg_messages_per_session || 0}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-purple-50 rounded-full">
              <Target className="w-6 h-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Topics Studied</p>
              <p className="text-2xl font-bold text-gray-900">
                {analyticsData?.topic_stats?.length || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Topic Performance */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Topic Performance</h3>
        </div>
        <div className="space-y-4">
          {analyticsData?.topic_stats?.length > 0 ? (
            analyticsData.topic_stats.map((topic, index) => (
              <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">{topic.topic}</h4>
                  <p className="text-sm text-gray-600">
                    {topic.completed_tasks} of {topic.total_tasks} tasks completed
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold text-gray-900">
                    {topic.completion_rate}%
                  </p>
                  <div className="w-24 bg-gray-200 rounded-full h-2 mt-1">
                    <div
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${topic.completion_rate}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-sm font-medium text-gray-900 mb-2">No topic data yet</h3>
              <p className="text-sm text-gray-500">
                Start creating study plans to see your topic performance.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Daily Completion */}
      <div className="card">
        <div className="card-header">
          <h3 className="card-title">Daily Task Completion</h3>
        </div>
        <div className="space-y-3">
          {analyticsData?.daily_completions?.length > 0 ? (
            analyticsData.daily_completions.slice(-7).map((day, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">
                    {new Date(day.date).toLocaleDateString('en-US', { 
                      weekday: 'short', 
                      month: 'short', 
                      day: 'numeric' 
                    })}
                  </p>
                  <p className="text-sm text-gray-600">
                    {day.completed} of {day.total} tasks
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-semibold text-gray-900">
                    {day.rate}%
                  </p>
                  <div className="w-20 bg-gray-200 rounded-full h-2 mt-1">
                    <div
                      className="bg-green-600 h-2 rounded-full transition-all"
                      style={{ width: `${day.rate}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8">
              <Calendar className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-sm font-medium text-gray-900 mb-2">No daily data yet</h3>
              <p className="text-sm text-gray-500">
                Complete tasks to see your daily progress.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Analytics; 