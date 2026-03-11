import { apiClient, API_ENDPOINTS } from './client';
import type { HistoryResponse, ToolHistoryResponse } from '../types/api';

/**
 * 获取会话历史
 */
export const getHistory = async (threadId: string): Promise<HistoryResponse> => {
  const response = await apiClient.get<HistoryResponse>(
    API_ENDPOINTS.HISTORY(threadId)
  );
  return response.data;
};

/**
 * 获取工具调用历史
 */
export const getToolHistory = async (threadId: string): Promise<ToolHistoryResponse> => {
  const response = await apiClient.get<ToolHistoryResponse>(
    API_ENDPOINTS.HISTORY_TOOLS(threadId)
  );
  return response.data;
};

/**
 * 删除会话历史
 */
export const deleteHistory = async (threadId: string): Promise<void> => {
  await apiClient.delete(API_ENDPOINTS.HISTORY(threadId));
};
