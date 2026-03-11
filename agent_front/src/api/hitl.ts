import { apiClient, API_ENDPOINTS } from './client';
import type {
  InterruptStatus,
  ResumeRequest,
  ResumeResponse
} from '../types/api';

/**
 * 获取中断状态
 */
export const getInterruptStatus = async (threadId: string): Promise<InterruptStatus> => {
  const response = await apiClient.get<InterruptStatus>(
    API_ENDPOINTS.HITL_STATUS(threadId)
  );
  return response.data;
};

/**
 * 恢复执行（批准操作）
 */
export const resumeExecution = async (request: ResumeRequest): Promise<ResumeResponse> => {
  const response = await apiClient.post<ResumeResponse>(
    API_ENDPOINTS.HITL_RESUME,
    request
  );
  return response.data;
};

/**
 * 批准操作
 */
export const approveOperation = async (
  threadId: string,
  reason?: string
): Promise<ResumeResponse> => {
  const url = reason
    ? `${API_ENDPOINTS.HITL_APPROVE(threadId)}?reason=${encodeURIComponent(reason)}`
    : API_ENDPOINTS.HITL_APPROVE(threadId);

  const response = await apiClient.post<ResumeResponse>(url);
  return response.data;
};

/**
 * 拒绝操作
 */
export const rejectOperation = async (
  threadId: string,
  reason?: string
): Promise<ResumeResponse> => {
  const url = reason
    ? `${API_ENDPOINTS.HITL_REJECT(threadId)}?reason=${encodeURIComponent(reason)}`
    : API_ENDPOINTS.HITL_REJECT(threadId);

  const response = await apiClient.post<ResumeResponse>(url);
  return response.data;
};
