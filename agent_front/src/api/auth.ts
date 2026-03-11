import { apiClient } from './client';

// 类型定义
export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface UpdateUserRequest {
  full_name?: string;
  avatar_url?: string;
}

export interface UserProfile {
  user: User;
  facts: Array<{ content: string; importance: number }>;
  preferences: Array<{ content: string; importance: number }>;
  skills: Array<{ content: string; importance: number }>;
  total_memories: number;
}

// API 调用
export const authAPI = {
  /**
   * 用户注册
   */
  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/api/auth/register', data);
    return response.data;
  },

  /**
   * 用户登录
   */
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/api/auth/login', data);
    return response.data;
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/api/auth/me');
    return response.data;
  },

  /**
   * 更新用户信息
   */
  updateUser: async (data: UpdateUserRequest): Promise<User> => {
    const response = await apiClient.put<User>('/api/auth/me', data);
    return response.data;
  },

  /**
   * 获取用户画像
   */
  getUserProfile: async (): Promise<UserProfile> => {
    const response = await apiClient.get<UserProfile>('/api/auth/profile');
    return response.data;
  },
};
