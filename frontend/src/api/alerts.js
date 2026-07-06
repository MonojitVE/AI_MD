import client from './client';

export const getAlertsList = async (filters = {}) => {
  const response = await client.get('/api/alerts', { params: filters });
  return response.data;
};

export const getAlertCounts = async () => {
  const response = await client.get('/api/alerts/count');
  return response.data;
};

export const markAlertRead = async (id) => {
  const response = await client.patch(`/api/alerts/${id}/read`);
  return response.data;
};

export const markAllAlertsRead = async () => {
  const response = await client.patch('/api/alerts/read-all');
  return response.data;
};

export const dismissAlert = async (id) => {
  const response = await client.patch(`/api/alerts/${id}/dismiss`);
  return response.data;
};

// CMMS Endpoints
export const acceptAlert = async (id) => {
  const response = await client.patch(`/api/alerts/${id}/accept`);
  return response.data;
};

export const startAlert = async (id) => {
  const response = await client.patch(`/api/alerts/${id}/start`);
  return response.data;
};

export const resolveAlert = async (id, data) => {
  const response = await client.patch(`/api/alerts/${id}/resolve`, data);
  return response.data;
};

export const verifyAlert = async (id) => {
  const response = await client.patch(`/api/alerts/${id}/verify`);
  return response.data;
};

export const createManualAlert = async (data) => {
  const response = await client.post('/api/alerts/manual', data);
  return response.data;
};
