import api from './api';

export const plannerService = {
  async createPlan(topics, targetDate, title) {
    return await api.post('/planner/create', { topics, target_date: targetDate, title });
  },

  async getPlans() {
    const response = await api.get('/planner/plans');
    return response.plans;
  },

  async getPlan(planId) {
    const response = await api.get(`/planner/plans/${planId}`);
    return response.plan;
  },

  async getTasksForDate(planId, date) {
    const response = await api.get(`/planner/plans/${planId}/tasks/${date}`);
    return response.tasks;
  },

  async updateTask(taskId, updates) {
    const response = await api.patch(`/planner/tasks/${taskId}`, updates);
    return response.task;
  },

  async deletePlan(planId) {
    return await api.delete(`/planner/plans/${planId}`);
  }
}; 