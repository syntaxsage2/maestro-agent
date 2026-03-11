import { useState, useEffect, useCallback } from 'react';
import { authAPI, type User, type LoginRequest, type RegisterRequest } from '../api/auth';
import { useChatStore } from '../store/chatStore';

const TOKEN_KEY = 'access_token';
const USER_KEY = 'user';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const { clearAllConversations } = useChatStore();

  // 从 localStorage 恢复登录状态
  useEffect(() => {
    const savedToken = localStorage.getItem(TOKEN_KEY);
    const savedUser = localStorage.getItem(USER_KEY);

    if (savedToken && savedUser) {
      try {
        const parsedUser = JSON.parse(savedUser);
        setToken(savedToken);
        setUser(parsedUser);
        setIsAuthenticated(true);
      } catch (error) {
        console.error('Failed to parse saved user:', error);
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
      }
    }

    setLoading(false);
  }, []);

  // 登录
  const login = useCallback(async (credentials: LoginRequest) => {
    try {
      const data = await authAPI.login(credentials);

      setToken(data.access_token);
      setUser(data.user);
      setIsAuthenticated(true);

      localStorage.setItem(TOKEN_KEY, data.access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(data.user));

      return data;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }, []);

  // 注册
  const register = useCallback(async (data: RegisterRequest) => {
    try {
      const response = await authAPI.register(data);

      setToken(response.access_token);
      setUser(response.user);
      setIsAuthenticated(true);

      localStorage.setItem(TOKEN_KEY, response.access_token);
      localStorage.setItem(USER_KEY, JSON.stringify(response.user));

      return response;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }, []);

  // 登出
  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);

    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);

    // 清空所有对话记录
    clearAllConversations();
  }, [clearAllConversations]);

  // 刷新用户信息
  const refreshUser = useCallback(async () => {
    if (!token) return;

    try {
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
      localStorage.setItem(USER_KEY, JSON.stringify(userData));
    } catch (error) {
      console.error('Failed to refresh user:', error);
      // Token 可能已过期，登出
      logout();
    }
  }, [token, logout]);

  // 更新用户信息
  const updateUser = useCallback(async (data: { full_name?: string; avatar_url?: string }) => {
    try {
      const updatedUser = await authAPI.updateUser(data);
      setUser(updatedUser);
      localStorage.setItem(USER_KEY, JSON.stringify(updatedUser));
      return updatedUser;
    } catch (error) {
      console.error('Failed to update user:', error);
      throw error;
    }
  }, []);

  return {
    user,
    token,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshUser,
    updateUser,
  };
}

// 获取 token 的工具函数（供 API client 使用）
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}
