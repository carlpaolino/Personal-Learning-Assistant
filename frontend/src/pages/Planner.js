import React, { useState, useEffect } from 'react';
import { Plus, Calendar, Target, Trash2 } from 'lucide-react';
import { plannerService } from '../services/plannerService';
import toast from 'react-hot-toast';

function Planner() {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    topics: '',
    targetDate: ''
  });

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const plansData = await plannerService.getPlans();
      setPlans(plansData);
    } catch (error) {
      toast.error('Failed to fetch study plans');
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePlan = async (e) => {
    e.preventDefault();
    
    if (!formData.title || !formData.topics || !formData.targetDate) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      const topics = formData.topics.split(',').map(topic => topic.trim()).filter(topic => topic);
      await plannerService.createPlan(topics, formData.targetDate, formData.title);
      
      toast.success('Study plan created successfully!');
      setShowCreateForm(false);
      setFormData({ title: '', topics: '', targetDate: '' });
      fetchPlans();
    } catch (error) {
      toast.error('Failed to create study plan');
    }
  };

  const handleDeletePlan = async (planId) => {
    if (window.confirm('Are you sure you want to delete this plan?')) {
      try {
        await plannerService.deletePlan(planId);
        toast.success('Plan deleted successfully');
        fetchPlans();
      } catch (error) {
        toast.error('Failed to delete plan');
      }
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Study Planner</h1>
          <p className="text-gray-600">Create and manage your study plans</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="btn btn-primary"
        >
          <Plus size={20} />
          Create Plan
        </button>
      </div>

      {/* Create Plan Form */}
      {showCreateForm && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">Create New Study Plan</h3>
            <button
              onClick={() => setShowCreateForm(false)}
              className="text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          </div>
          <form onSubmit={handleCreatePlan} className="space-y-4">
            <div className="form-group">
              <label className="form-label">Plan Title</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., Math Exam Preparation"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Topics (comma-separated)</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g., Algebra, Geometry, Calculus"
                value={formData.topics}
                onChange={(e) => setFormData({ ...formData, topics: e.target.value })}
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Target Date</label>
              <input
                type="date"
                className="form-input"
                value={formData.targetDate}
                onChange={(e) => setFormData({ ...formData, targetDate: e.target.value })}
              />
            </div>
            
            <div className="flex gap-3">
              <button type="submit" className="btn btn-primary">
                Create Plan
              </button>
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="btn btn-outline"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Plans List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {plans.map((plan) => (
          <div key={plan.id} className="card">
            <div className="card-header">
              <h3 className="card-title">{plan.title}</h3>
              <button
                onClick={() => handleDeletePlan(plan.id)}
                className="text-red-500 hover:text-red-700"
              >
                <Trash2 size={16} />
              </button>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Target size={16} />
                <span>{plan.topics?.length || 0} topics</span>
              </div>
              
              <div className="flex items-center gap-2 text-sm text-gray-600">
                <Calendar size={16} />
                <span>Target: {new Date(plan.target_date).toLocaleDateString()}</span>
              </div>
              
              <div className="pt-3 border-t">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Progress</span>
                  <span className="font-medium">
                    {plan.tasks?.filter(task => task.status === 'completed').length || 0} / {plan.tasks?.length || 0}
                  </span>
                </div>
                <div className="mt-2 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all"
                    style={{
                      width: `${plan.tasks?.length > 0 
                        ? (plan.tasks.filter(task => task.status === 'completed').length / plan.tasks.length) * 100 
                        : 0}%`
                    }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {plans.length === 0 && !showCreateForm && (
        <div className="text-center py-12">
          <Calendar className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No study plans</h3>
          <p className="mt-1 text-sm text-gray-500">
            Get started by creating your first study plan.
          </p>
          <div className="mt-6">
            <button
              onClick={() => setShowCreateForm(true)}
              className="btn btn-primary"
            >
              <Plus size={20} />
              Create Plan
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default Planner; 