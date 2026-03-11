import { create } from 'zustand';
import type { Conversation, Message, NodeType } from '../types/api';
import {
  loadConversations,
  saveConversations,
  loadCurrentConversationId,
  saveCurrentConversationId
} from '../utils/storage';

interface ChatStore {
  // 状态
  conversations: Conversation[];
  currentConversationId: string | null;
  isStreaming: boolean;
  currentNode: NodeType | null;
  showSidebar: boolean;

  // Actions
  initStore: () => void;
  addConversation: (conversation: Conversation) => void;
  updateConversation: (id: string, updates: Partial<Conversation>) => void;
  deleteConversation: (id: string) => void;
  setCurrentConversation: (id: string | null) => void;
  getCurrentConversation: () => Conversation | null;
  addMessage: (conversationId: string, message: Message) => void;
  updateLastMessage: (conversationId: string, content: string) => void;
  setIsStreaming: (isStreaming: boolean) => void;
  setCurrentNode: (node: NodeType | null) => void;
  toggleSidebar: () => void;
  clearAllConversations: () => void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  // 初始状态
  conversations: [],
  currentConversationId: null,
  isStreaming: false,
  currentNode: null,
  showSidebar: true,

  // 初始化 Store（从 localStorage 加载数据）
  initStore: () => {
    const conversations = loadConversations();
    const currentConversationId = loadCurrentConversationId();
    set({ conversations, currentConversationId });
  },

  // 添加新会话
  addConversation: (conversation) => {
    set((state) => {
      const newConversations = [...state.conversations, conversation];
      saveConversations(newConversations);
      saveCurrentConversationId(conversation.id);
      return {
        conversations: newConversations,
        currentConversationId: conversation.id,
      };
    });
  },

  // 更新会话
  updateConversation: (id, updates) => {
    set((state) => {
      const newConversations = state.conversations.map((conv) =>
        conv.id === id ? { ...conv, ...updates } : conv
      );
      saveConversations(newConversations);
      return { conversations: newConversations };
    });
  },

  // 删除会话
  deleteConversation: (id) => {
    set((state) => {
      const newConversations = state.conversations.filter((conv) => conv.id !== id);
      saveConversations(newConversations);

      // 如果删除的是当前会话，切换到第一个会话
      const newCurrentId = state.currentConversationId === id
        ? (newConversations[0]?.id || null)
        : state.currentConversationId;

      saveCurrentConversationId(newCurrentId);

      return {
        conversations: newConversations,
        currentConversationId: newCurrentId,
      };
    });
  },

  // 设置当前会话
  setCurrentConversation: (id) => {
    saveCurrentConversationId(id);
    set({ currentConversationId: id });
  },

  // 获取当前会话
  getCurrentConversation: () => {
    const { conversations, currentConversationId } = get();
    return conversations.find((conv) => conv.id === currentConversationId) || null;
  },

  // 添加消息到指定会话
  addMessage: (conversationId, message) => {
    set((state) => {
      const newConversations = state.conversations.map((conv) =>
        conv.id === conversationId
          ? {
              ...conv,
              messages: [...conv.messages, message],
              lastUpdated: Date.now(),
              // 如果是第一条消息，更新标题
              title: conv.messages.length === 0
                ? message.content.slice(0, 30) + (message.content.length > 30 ? '...' : '')
                : conv.title,
            }
          : conv
      );
      saveConversations(newConversations);
      return { conversations: newConversations };
    });
  },

  // 更新最后一条消息（用于流式响应）
  updateLastMessage: (conversationId, content) => {
    set((state) => {
      const newConversations = state.conversations.map((conv) => {
        if (conv.id !== conversationId) return conv;

        const messages = [...conv.messages];
        if (messages.length > 0) {
          const lastMessage = messages[messages.length - 1];
          messages[messages.length - 1] = {
            ...lastMessage,
            content: content,
          };
        }

        return {
          ...conv,
          messages,
          lastUpdated: Date.now(),
        };
      });

      saveConversations(newConversations);
      return { conversations: newConversations };
    });
  },

  // 设置流式响应状态
  setIsStreaming: (isStreaming) => set({ isStreaming }),

  // 设置当前节点
  setCurrentNode: (node) => set({ currentNode: node }),

  // 切换侧边栏显示
  toggleSidebar: () => set((state) => ({ showSidebar: !state.showSidebar })),

  // 清空所有会话
  clearAllConversations: () => {
    saveConversations([]);
    saveCurrentConversationId(null);
    set({
      conversations: [],
      currentConversationId: null,
    });
  },
}));
