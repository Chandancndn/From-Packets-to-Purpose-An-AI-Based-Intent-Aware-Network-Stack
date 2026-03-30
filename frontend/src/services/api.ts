import axios from 'axios';
import { Flow, FlowStatistics, PredictionResult, QoSStats, CategoryConfig } from '../types';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Flow API
export const getFlows = async (
  skip = 0,
  limit = 100,
  category?: string,
  minConfidence?: number
): Promise<Flow[]> => {
  const params = new URLSearchParams();
  params.append('skip', skip.toString());
  params.append('limit', limit.toString());
  if (category) params.append('category', category);
  if (minConfidence) params.append('min_confidence', minConfidence.toString());

  const response = await api.get(`/flows?${params.toString()}`);
  return response.data;
};

export const getFlow = async (id: number): Promise<Flow> => {
  const response = await api.get(`/flows/${id}`);
  return response.data;
};

export const getStatistics = async (): Promise<FlowStatistics> => {
  const response = await api.get('/flows/stats/summary');
  return response.data;
};

// Prediction API
export const classifyFlow = async (flowData: unknown): Promise<PredictionResult> => {
  const response = await api.post('/prediction/classify', flowData);
  return response.data;
};

export const getCategories = async (): Promise<CategoryConfig> => {
  const response = await api.get('/prediction/categories');
  return response.data;
};

export const getModelStatus = async (): Promise<unknown> => {
  const response = await api.get('/prediction/model/status');
  return response.data;
};

// QoS API
export const getQoSStatus = async (): Promise<QoSStats> => {
  const response = await api.get('/qos/status');
  return response.data;
};

export const getQoSConfig = async (): Promise<unknown> => {
  const response = await api.get('/qos/config');
  return response.data;
};

export const initializeQoS = async (): Promise<{ status: string; message: string }> => {
  const response = await api.post('/qos/initialize');
  return response.data;
};

// Health Check
export const getHealth = async (): Promise<{
  status: string;
  capture_engine: { is_capturing: boolean };
  ml_model: { is_ready: boolean };
}> => {
  const response = await api.get('/health');
  return response.data;
};

export default api;