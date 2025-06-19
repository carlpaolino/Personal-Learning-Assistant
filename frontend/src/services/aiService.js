import api from './api';

export const aiService = {
  async explainTopic(topic, personaLevel = 'student', maxWords = 500) {
    const response = await api.post('/ai/explain', { topic, persona_level: personaLevel, max_words: maxWords });
    return response;
  },

  async generateQuiz(topic, numQuestions = 5) {
    const response = await api.post('/ai/quiz', { topic, num_questions: numQuestions });
    return response;
  },

  async chat(message, sessionId = null) {
    const response = await api.post('/ai/chat', { message, session_id: sessionId });
    return response;
  },

  async getChatHistory(sessionId) {
    const response = await api.get(`/ai/chat/history/${sessionId}`);
    return response.messages;
  },

  async getChatSessions() {
    const response = await api.get('/ai/chat/sessions');
    return response.sessions;
  }
}; 