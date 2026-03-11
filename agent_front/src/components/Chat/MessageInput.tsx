import { useState, useRef, KeyboardEvent } from 'react';
import { Send, Paperclip, Image as ImageIcon, Mic } from 'lucide-react';
import { useChat } from '../../hooks/useChat';
import { useChatStore } from '../../store/chatStore';
import { ImageUpload } from './ImageUpload';
import { useHITL } from '../../hooks/useHITL';

export const MessageInput = () => {
  const [message, setMessage] = useState('');
  const [showImageUpload, setShowImageUpload] = useState(false);
  const [images, setImages] = useState<File[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const { sendTextMessage, sendImageMessage, isLoading } = useChat();
  const { isStreaming, getCurrentConversation } = useChatStore();
  const { startPolling } = useHITL({
    threadId: getCurrentConversation()?.id || null
  });

  const handleSend = async () => {
    if (!message.trim() && images.length === 0) return;
    if (isStreaming || isLoading) return;

    const content = message.trim();
    setMessage('');
    setImages([]);
    setShowImageUpload(false);

    // 重置文本框高度
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    try {
      if (images.length > 0) {
        await sendImageMessage(content, images);
      } else {
        await sendTextMessage(content);
      }

      // 发送后延迟 2 秒开始轮询 HITL 状态（给后端处理时间）
      setTimeout(() => {
        startPolling();
      }, 2000);
    } catch (error) {
      console.error('Send message error:', error);
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);

    // 自动调整高度
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
  };

  return (
    <div className="border-t border-gray-800 bg-primary/50 backdrop-blur-sm p-4">
      {showImageUpload && (
        <div className="mb-4">
          <ImageUpload
            onImagesChange={setImages}
            maxImages={5}
            maxSize={10 * 1024 * 1024}
          />
        </div>
      )}

      <div className="max-w-4xl mx-auto">
        <div className="flex items-end gap-3 bg-secondary/70 backdrop-blur-sm border border-gray-800 rounded-2xl p-3 focus-within:border-accent transition-colors">
          <button
            onClick={() => setShowImageUpload(!showImageUpload)}
            className={`p-2 rounded-lg transition-colors ${
              showImageUpload ? 'bg-accent text-white' : 'hover:bg-gray-700 text-gray-400'
            }`}
            disabled={isStreaming || isLoading}
            aria-label="上传图片"
          >
            <ImageIcon className="w-5 h-5" />
          </button>

          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder="输入消息... (Enter 发送，Shift+Enter 换行)"
            className="flex-1 bg-transparent outline-none resize-none text-gray-100 placeholder-gray-500 min-h-[29px] max-h-[200px]"
            rows={1}
            disabled={isStreaming || isLoading}
          />

          <button
            onClick={handleSend}
            disabled={(!message.trim() && images.length === 0) || isStreaming || isLoading}
            className={`
              p-2 rounded-lg transition-all
              ${(!message.trim() && images.length === 0) || isStreaming || isLoading
                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                : 'bg-accent hover:bg-accent-light text-white hover:rotate-12'
              }
            `}
            aria-label="发送消息"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>

        <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
          <div className="flex items-center gap-4">
            <button
              className="flex items-center gap-2 hover:text-accent transition-colors"
              disabled={isStreaming || isLoading}
            >
              <Paperclip className="w-4 h-4" />
              <span>上传文件</span>
            </button>
            <button
              onClick={() => setShowImageUpload(!showImageUpload)}
              className="flex items-center gap-2 hover:text-accent transition-colors"
              disabled={isStreaming || isLoading}
            >
              <ImageIcon className="w-4 h-4" />
              <span>添加图片</span>
            </button>
            <button
              className="flex items-center gap-2 hover:text-accent transition-colors"
              disabled={isStreaming || isLoading}
            >
              <Mic className="w-4 h-4" />
              <span>语音输入</span>
            </button>
          </div>

          {isStreaming && (
            <span className="text-accent">正在生成回复...</span>
          )}
        </div>
      </div>
    </div>
  );
};
