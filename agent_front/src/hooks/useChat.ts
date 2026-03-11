import { useState } from 'react';
import { toast } from 'react-hot-toast';
import { useChatStore } from '../store/chatStore';
import { useAuth } from './useAuth';
import { useSSE } from './useSSE';
import { sendMultimodalMessage } from '../api/chat';
import type { Message, SSEEvent } from '../types/api';

export const useChat = () => {
  const [isLoading, setIsLoading] = useState(false);
  const { streamChat } = useSSE();
  const { user } = useAuth();

  const {
    getCurrentConversation,
    addMessage,
    updateLastMessage,
    setIsStreaming,
    setCurrentNode,
    addConversation,
  } = useChatStore();

  /**
   * 发送文本消息（流式）
   */
  const sendTextMessage = async (content: string) => {
    console.log('🚀 Called sendTextMessage with content:', content);
    const currentConv = getCurrentConversation();
    let threadId = currentConv?.id;

    // 如果没有当前会话，创建新会话
    if (!currentConv) {
      const newConvId = `thread_${Date.now()}`;
      addConversation({
        id: newConvId,
        title: content.slice(0, 30) + (content.length > 30 ? '...' : ''),
        messages: [],
        lastUpdated: Date.now(),
      });
      threadId = newConvId;
    }

    if (!threadId) return;

    // 添加用户消息
    const userMessage: Message = {
      role: 'human',
      content,
      timestamp: Date.now(),
    };
    addMessage(threadId, userMessage);

    // 添加空的 AI 消息占位
    const aiMessage: Message = {
      role: 'ai',
      content: '',
      timestamp: Date.now(),
    };
    addMessage(threadId, aiMessage);

    setIsStreaming(true);
    setIsLoading(true);

    let accumulatedContent = '';

    try {
      await streamChat(
        {
          message: content,
          thread_id: threadId,
          user_id: user?.id ? String(user.id) : undefined,
          stream: true,
        },
        {
          onEvent: (event: SSEEvent) => {
            switch (event.event) {
              case 'node_start':
                if ('node' in event) {
                  setCurrentNode(event.node as any);
                }
                break;

              case 'node_end':
                setCurrentNode(null);
                break;

              case 'message':
                if ('content' in event && event.content) {
                  accumulatedContent = event.content;
                  updateLastMessage(threadId!, accumulatedContent);
                }
                break;

              case 'token':
                if ('content' in event && event.content) {
                  accumulatedContent += event.content;
                  updateLastMessage(threadId!, accumulatedContent);
                }
                break;

              case 'done':
                setIsStreaming(false);
                setCurrentNode(null);
                setIsLoading(false);
                break;

              case 'error':
                if ('data' in event && event.data) {
                  toast.error(event.data.error || '发生错误');
                }
                break;
            }
          },

          onError: (error) => {
            toast.error(error.message || '发送失败');
            setIsStreaming(false);
            setCurrentNode(null);
            setIsLoading(false);
          },

          onComplete: () => {
            setIsStreaming(false);
            setCurrentNode(null);
            setIsLoading(false);
          },
        }
      );
    } catch (error) {
      console.error('Send message error:', error);
      toast.error('发送消息失败');
      setIsStreaming(false);
      setCurrentNode(null);
      setIsLoading(false);
    }
  };

  /**
   * 发送多模态消息（图片）
   */
  const sendImageMessage = async (content: string, files: File[]) => {
    const currentConv = getCurrentConversation();
    let threadId = currentConv?.id;

    // 如果没有当前会话，创建新会话
    if (!currentConv) {
      const newConvId = `thread_${Date.now()}`;
      addConversation({
        id: newConvId,
        title: content.slice(0, 30) + (content.length > 30 ? '...' : ''),
        messages: [],
        lastUpdated: Date.now(),
      });
      threadId = newConvId;
    }

    if (!threadId) return;

    setIsLoading(true);

    try {
      // 添加用户消息（含图片）
      const userMessage: Message = {
        role: 'human',
        content,
        timestamp: Date.now(),
        images: files.map(f => URL.createObjectURL(f)),
      };
      addMessage(threadId, userMessage);

      // 调用多模态 API
      const response = await sendMultimodalMessage(
        content,
        files,
        threadId,
        user?.id ? String(user.id) : undefined
      );

      // 添加 AI 响应
      const aiMessage: Message = {
        role: 'ai',
        content: response.message,
        timestamp: Date.now(),
      };
      addMessage(threadId, aiMessage);

      toast.success('图片已发送');
    } catch (error) {
      console.error('Send image message error:', error);
      toast.error('发送图片失败');
    } finally {
      setIsLoading(false);
    }
  };

  return {
    sendTextMessage,
    sendImageMessage,
    isLoading,
  };
};
