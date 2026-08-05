import { defineStore } from 'pinia';
import api from '../services/api';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('alfie_client_token') || null,
    role: null,
    tenantId: localStorage.getItem('alfie_tenant_id') || null,
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
        this.tenantId = response.data.tenant_id;
        
        localStorage.setItem('alfie_client_token', this.token);
        localStorage.setItem('alfie_tenant_id', this.tenantId);
        return true;
      } catch (error) {
        console.error("Login failed", error);
        return false;
      }
    },
    logout() {
      this.token = null;
      this.role = null;
      this.tenantId = null;
      localStorage.removeItem('alfie_client_token');
      localStorage.removeItem('alfie_tenant_id');
    }
  }
});
