import { apiClient, API_ENDPOINTS } from './client';
import type { HealthResponse, ToolsResponse } from '../types/api';

/**
 * 健康检查
 */
export const checkHealth = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>(API_ENDPOINTS.HEALTH);
  return response.data;
};

/**
 * 获取工具列表
 */
export const getTools = async (): Promise<ToolsResponse> => {
  const response = await apiClient.get<ToolsResponse>(API_ENDPOINTS.TOOLS);
  return response.data;
};
