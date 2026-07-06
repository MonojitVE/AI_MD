import { create } from 'zustand';
import { login as apiLogin, verify as apiVerify, logout as apiLogout } from '../api/auth';
import api from '../api/client';

const TOKEN_KEY = 'sentry_fab_admin_token';

const useAuthStore = create((set, get) => ({
  user: null,
  isAdmin: false,
  token: localStorage.getItem(TOKEN_KEY) || null,
  loading: false,
  error: null,

  login: async (employeeId, password) => {
    set({ loading: true, error: null });
    try {
      const data = await apiLogin(employeeId, password);
      localStorage.setItem(TOKEN_KEY, data.access_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
      
      const user = await apiVerify();
      set({ user, isAdmin: user.role === 'admin', token: data.access_token, loading: false });
      return data;
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed';
      set({ loading: false, error: message });
      throw new Error(message);
    }
  },

  checkAuth: async () => {
    const token = get().token;
    if (!token) {
      set({ user: null, isAdmin: false });
      return;
    }
    try {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      const user = await apiVerify();
      set({ user, isAdmin: user.role === 'admin' });
    } catch {
      localStorage.removeItem(TOKEN_KEY);
      delete api.defaults.headers.common['Authorization'];
      set({ user: null, isAdmin: false, token: null });
    }
  },

  logout: async () => {
    try {
      await apiLogout();
    } catch {}
    localStorage.removeItem(TOKEN_KEY);
    delete api.defaults.headers.common['Authorization'];
    set({ user: null, isAdmin: false, token: null, error: null });
  },

  clearError: () => set({ error: null }),
}));

export default useAuthStore;
