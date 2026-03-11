import { useEffect, useRef } from 'react';
import { MessageItem } from './MessageItem';
import { NodeStatus } from './NodeStatus';
import { useChatStore } from '../../store/chatStore';
import { Loader2 } from 'lucide-react';

export const MessageList = () => {
  const { getCurrentConversation, currentNode, isStreaming } = useChatStore();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const conversation = getCurrentConversation();

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation?.messages, isStreaming]);

  if (!conversation) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🤖</div>
          <h2 className="text-2xl font-bold mb-2 bg-gradient-to-r from-accent-light to-blue-400 text-transparent bg-clip-text">
            AI Agent 智能助手
          </h2>
          <p className="text-gray-400 mb-6">您好！我是您的 AI 助手。有什么可以帮您的吗？</p>

          <div className="grid grid-cols-2 gap-3 max-w-md mx-auto">
            <div className="bg-secondary/50 backdrop-blur-sm border border-gray-800 rounded-xl p-4 text-left hover:border-accent transition-colors cursor-pointer">
              <div className="text-2xl mb-2">💡</div>
              <h3 className="text-sm font-semibold mb-1">创意构思</h3>
              <p className="text-xs text-gray-500">帮你激发灵感</p>
            </div>
            <div className="bg-secondary/50 backdrop-blur-sm border border-gray-800 rounded-xl p-4 text-left hover:border-accent transition-colors cursor-pointer">
              <div className="text-2xl mb-2">📝</div>
              <h3 className="text-sm font-semibold mb-1">文档分析</h3>
              <p className="text-xs text-gray-500">理解文档内容</p>
            </div>
            <div className="bg-secondary/50 backdrop-blur-sm border border-gray-800 rounded-xl p-4 text-left hover:border-accent transition-colors cursor-pointer">
              <div className="text-2xl mb-2">💻</div>
              <h3 className="text-sm font-semibold mb-1">代码生成</h3>
              <p className="text-xs text-gray-500">编写高质量代码</p>
            </div>
            <div className="bg-secondary/50 backdrop-blur-sm border border-gray-800 rounded-xl p-4 text-left hover:border-accent transition-colors cursor-pointer">
              <div className="text-2xl mb-2">🔍</div>
              <h3 className="text-sm font-semibold mb-1">网页搜索</h3>
              <p className="text-xs text-gray-500">获取最新信息</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar px-6 py-6">
      <div className="max-w-4xl mx-auto">
        {conversation.messages.map((message, index) => (
          <MessageItem key={index} message={message} />
        ))}

        {currentNode && (
          <div className="flex justify-start mb-6">
            <NodeStatus node={currentNode} />
          </div>
        )}

        {isStreaming && !currentNode && (
          <div className="flex items-center gap-2 text-gray-400">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">正在生成回复...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};
