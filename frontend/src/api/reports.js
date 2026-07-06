import api from './client';

export const getAiReports = async (type = null) => {
  const url = type ? `/api/ai-reports?report_type=${type}` : '/api/ai-reports';
  const response = await api.get(url);
  return response.data;
};

export const getAiReportDetail = async (id) => {
  const response = await api.get(`/api/ai-reports/${id}`);
  return response.data;
};

export const generateAiReport = async (type) => {
  const response = await api.post(`/api/ai-reports/generate?report_type=${type}`);
  return response.data;
};
