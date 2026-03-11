import { apiClient, API_ENDPOINTS } from './client';
import type {
  ChatRequest,
  ChatResponse,
  MultimodalChatResponse
} from '../types/api';

/**
 * 发送普通文本消息
 */
export const sendMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await apiClient.post<ChatResponse>(API_ENDPOINTS.CHAT, request);
  return response.data;
};

/**
 * 发送多模态消息（文件上传）
 * @param message - 消息内容
 * @param files - 文件列表
 * @param threadId - 会话ID
 * @param userId - 用户ID（从 user.id 获取）
 */
export const sendMultimodalMessage = async (
  message: string,
  files: File[],
  threadId?: string,
  userId?: string
): Promise<MultimodalChatResponse> => {
  const formData = new FormData();
  formData.append('message', message);

  files.forEach(file => {
    formData.append('files', file);
  });

  if (threadId) {
    formData.append('thread_id', threadId);
  }

  if (userId) {
    formData.append('user_id', userId);
  }

  const response = await apiClient.post<MultimodalChatResponse>(
    API_ENDPOINTS.CHAT_MULTIMODAL,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  return response.data;
};

/**
 * 获取 SSE 流式聊天 URL
 */
export const getStreamChatUrl = (): string => {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  return `${baseUrl}${API_ENDPOINTS.CHAT_STREAM}`;
};
