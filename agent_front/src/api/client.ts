import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000');

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加 JWT token
apiClient.interceptors.request.use(
  (config) => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('access_token');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理错误和 token 过期
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);

    if (error.response) {
      // Token 过期或无效
      if (error.response.status === 401) {
        // 清除本地存储的认证信息
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');

        // 如果当前不在登录页，跳转到登录页
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/';
        }

        return Promise.reject(new Error('登录已过期，请重新登录'));
      }

      // 服务器返回错误
      const errorMessage = error.response.data?.detail || '服务器错误';
      return Promise.reject(new Error(errorMessage));
    } else if (error.request) {
      // 请求已发送但没有收到响应
      return Promise.reject(new Error('网络错误，请检查服务器是否运行'));
    } else {
      // 其他错误
      return Promise.reject(error);
    }
  }
);

export const API_ENDPOINTS = {
  // 认证相关
  AUTH_REGISTER: '/api/auth/register',
  AUTH_LOGIN: '/api/auth/login',
  AUTH_ME: '/api/auth/me',
  AUTH_PROFILE: '/api/auth/profile',

  // 聊天相关
  CHAT: '/api/chat',
  CHAT_STREAM: '/api/chat/stream',
  CHAT_MULTIMODAL: '/api/chat/multimodal',
  CHAT_MULTIMODAL_JSON: '/api/chat/multimodal/json',

  // 历史相关
  HISTORY: (threadId: string) => `/api/history/${threadId}`,
  HISTORY_TOOLS: (threadId: string) => `/api/history/${threadId}/tools`,

  // HITL 相关
  HITL_STATUS: (threadId: string) => `/api/hitl/status/${threadId}`,
  HITL_RESUME: '/api/hitl/resume',
  HITL_APPROVE: (threadId: string) => `/api/hitl/approve/${threadId}`,
  HITL_REJECT: (threadId: string) => `/api/hitl/reject/${threadId}`,

  // 状态相关
  STATE: (threadId: string) => `/api/state/${threadId}`,
  STATE_HISTORY: (threadId: string) => `/api/state/${threadId}/history`,
  STATE_ROLLBACK: (threadId: string) => `/api/state/${threadId}/rollback`,

  // 系统相关
  HEALTH: '/health',
  TOOLS: '/tools',
} as const;
