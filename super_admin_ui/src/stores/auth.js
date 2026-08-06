import { defineStore } from 'pinia';
import api from '../services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('alfie_super_token') || null,
    role: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(email, password) {
      try {
        const response = await api.post('/api/auth/login', { email, password });
        this.token = response.data.access_token;
        this.role = response.data.role;
        localStorage.setItem('alfie_super_token', this.token);
        return true;
      } catch (error) {
        console.error("Login failed", error);
        return false;
      }
    },
    logout() {
      this.token = null;
      this.role = null;
      localStorage.removeItem('alfie_super_token');
    }
  }
});
