import api from './api';

export const authService = {
  async login(email, password) {
    return await api.post('/auth/login', { email, password });
  },

  async register(email, password, persona = 'student') {
    return await api.post('/auth/register', { email, password, persona });
  },

  async getProfile() {
    const response = await api.get('/auth/profile');
    return response.user;
  },

  async updateProfile(updates) {
    const response = await api.put('/auth/profile', updates);
    return response.user;
  }
}; 