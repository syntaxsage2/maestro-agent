import type { Conversation } from '../types/api';

const STORAGE_KEYS = {
  CONVERSATIONS: 'intentrouter_conversations',
  CURRENT_CONVERSATION_ID: 'intentrouter_current_conversation_id',
  USER_ID: 'intentrouter_user_id',
  THEME: 'intentrouter_theme',
} as const;

/**
 * 保存会话列表
 */
export const saveConversations = (conversations: Conversation[]): void => {
  try {
    localStorage.setItem(STORAGE_KEYS.CONVERSATIONS, JSON.stringify(conversations));
  } catch (error) {
    console.error('Failed to save conversations:', error);
  }
};

/**
 * 加载会话列表
 */
export const loadConversations = (): Conversation[] => {
  try {
    const data = localStorage.getItem(STORAGE_KEYS.CONVERSATIONS);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Failed to load conversations:', error);
    return [];
  }
};

/**
 * 保存当前会话ID
 */
export const saveCurrentConversationId = (id: string | null): void => {
  try {
    if (id) {
      localStorage.setItem(STORAGE_KEYS.CURRENT_CONVERSATION_ID, id);
    } else {
      localStorage.removeItem(STORAGE_KEYS.CURRENT_CONVERSATION_ID);
    }
  } catch (error) {
    console.error('Failed to save current conversation ID:', error);
  }
};

/**
 * 加载当前会话ID
 */
export const loadCurrentConversationId = (): string | null => {
  try {
    return localStorage.getItem(STORAGE_KEYS.CURRENT_CONVERSATION_ID);
  } catch (error) {
    console.error('Failed to load current conversation ID:', error);
    return null;
  }
};

/**
 * 保存用户ID
 */
export const saveUserId = (userId: string): void => {
  try {
    localStorage.setItem(STORAGE_KEYS.USER_ID, userId);
  } catch (error) {
    console.error('Failed to save user ID:', error);
  }
};

/**
 * 加载用户ID
 */
export const loadUserId = (): string | null => {
  try {
    return localStorage.getItem(STORAGE_KEYS.USER_ID);
  } catch (error) {
    console.error('Failed to load user ID:', error);
    return null;
  }
};

/**
 * 保存主题设置
 */
export const saveTheme = (theme: 'light' | 'dark'): void => {
  try {
    localStorage.setItem(STORAGE_KEYS.THEME, theme);
  } catch (error) {
    console.error('Failed to save theme:', error);
  }
};

/**
 * 加载主题设置
 */
export const loadTheme = (): 'light' | 'dark' => {
  try {
    const theme = localStorage.getItem(STORAGE_KEYS.THEME);
    return (theme === 'light' || theme === 'dark') ? theme : 'dark';
  } catch (error) {
    console.error('Failed to load theme:', error);
    return 'dark';
  }
};

/**
 * 清空所有存储数据
 */
export const clearAllStorage = (): void => {
  try {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
  } catch (error) {
    console.error('Failed to clear storage:', error);
  }
};
