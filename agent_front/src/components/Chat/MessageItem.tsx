import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import { Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import { toast } from 'react-hot-toast';
import type { Message } from '../../types/api';
import { formatRelativeTime } from '../../utils/time';

interface MessageItemProps {
  message: Message;
}

export const MessageItem = ({ message }: MessageItemProps) => {
  const isUser = message.role === 'human';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    toast.success('已复制到剪贴板');
  };

  return (
    <div className={`flex gap-4 mb-6 animate-fadeIn ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="flex-shrink-0 w-9 h-9 rounded-full bg-accent flex items-center justify-center">
          <span className="text-white text-lg">🤖</span>
        </div>
      )}

      <div className={`flex flex-col gap-2 max-w-[80%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`
            px-4 py-3 rounded-2xl shadow-lg
            ${isUser
              ? 'bg-gradient-to-r from-userBubble to-blue-600 text-white rounded-br-sm'
              : 'bg-aiBubble text-gray-100 rounded-bl-sm'
            }
          `}
        >
          {message.images && message.images.length > 0 && (
            <div className="mb-3 flex flex-wrap gap-2">
              {message.images.map((img, index) => (
                <img
                  key={index}
                  src={img}
                  alt={`上传图片 ${index + 1}`}
                  className="max-w-xs rounded-lg"
                />
              ))}
            </div>
          )}

          <div className="prose prose-invert prose-sm max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={oneDark}
                      language={match[1]}
                      PreTag="div"
                      className="rounded-lg !bg-gray-900 !mt-2"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className="bg-gray-800 px-1.5 py-0.5 rounded text-sm" {...props}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs text-gray-500">
          <span>
            {isUser ? '我' : 'AI 助手'} {message.timestamp ? formatRelativeTime(message.timestamp) : '刚刚'}
          </span>

          {!isUser && (
            <>
              <button
                onClick={handleCopy}
                className="hover:text-accent transition-colors"
                aria-label="复制消息"
              >
                <Copy className="w-3.5 h-3.5" />
              </button>
              <button
                className="hover:text-accent transition-colors"
                aria-label="赞"
              >
                <ThumbsUp className="w-3.5 h-3.5" />
              </button>
              <button
                className="hover:text-accent transition-colors"
                aria-label="踩"
              >
                <ThumbsDown className="w-3.5 h-3.5" />
              </button>
            </>
          )}
        </div>
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
          <span className="text-white text-lg">👤</span>
        </div>
      )}
    </div>
  );
};
