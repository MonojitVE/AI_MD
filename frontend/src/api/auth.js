import api from './client';

export const login = async (employee_id, password) => {
  const response = await api.post('/api/auth/login', { employee_id, password });
  return response.data;
};

export const register = async (userData) => {
  const response = await api.post('/api/auth/register', userData);
  return response.data;
};

export const verify = async () => {
  const response = await api.get('/api/auth/me');
  return response.data;
};

export const logout = async () => {
  const response = await api.post('/api/auth/logout');
  return response.data;
};
