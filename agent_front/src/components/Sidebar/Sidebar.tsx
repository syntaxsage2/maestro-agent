import { MessageSquare, Trash2, Star } from 'lucide-react';
import { useChatStore } from '../../store/chatStore';
import { formatRelativeTime } from '../../utils/time';

export const Sidebar = () => {
  const {
    conversations,
    currentConversationId,
    setCurrentConversation,
    deleteConversation
  } = useChatStore();

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm('确定要删除对话吗')) {
      deleteConversation(id);
    }
  };

  return (
    <aside className="w-80 bg-secondary/70 backdrop-blur-sm border-r border-gray-800 flex flex-col">
      <div className="p-4 border-b border-gray-800">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider flex items-center gap-2">
          <MessageSquare className="w-4 h-4" />
          历史对话
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
        {conversations.length === 0 ? (
          <div className="text-center text-gray-500 mt-8 px-4">
            <p className="text-sm">没有对话</p>
            <p className="text-xs mt-2">点击"新对话"开始对话</p>
          </div>
        ) : (
          <div className="space-y-1">
            {conversations
              .slice()
              .reverse()
              .map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => setCurrentConversation(conv.id)}
                  className={`
                    group relative p-3 rounded-lg cursor-pointer transition-all
                    ${currentConversationId === conv.id
                      ? 'bg-accent text-white'
                      : 'hover:bg-gray-800/50'
                    }
                  `}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <h3 className={`
                        text-sm font-medium truncate
                        ${currentConversationId === conv.id ? 'text-white' : 'text-gray-200'}
                      `}>
                        {conv.title}
                      </h3>
                      <p className={`
                        text-xs mt-1
                        ${currentConversationId === conv.id ? 'text-white/70' : 'text-gray-500'}
                      `}>
                        {formatRelativeTime(conv.lastUpdated)} {conv.messages.length} 条消息
                      </p>
                    </div>

                    <button
                      onClick={(e) => handleDelete(conv.id, e)}
                      className={`
                        p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity
                        ${currentConversationId === conv.id
                          ? 'hover:bg-white/20'
                          : 'hover:bg-gray-700'
                        }
                      `}
                      aria-label="删除对话"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
          </div>
        )}
      </div>

      <div className="p-4 border-t border-gray-800">
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-primary/50 rounded-lg p-3 text-center">
            <div className="text-accent text-xl mb-1">➕</div>
            <div className="text-xs text-gray-400">新对话</div>
          </div>
          <div className="bg-primary/50 rounded-lg p-3 text-center">
            <div className="text-accent text-xl mb-1">🔍</div>
            <div className="text-xs text-gray-400">网页搜索</div>
          </div>
          <div className="bg-primary/50 rounded-lg p-3 text-center">
            <div className="text-accent text-xl mb-1">📄</div>
            <div className="text-xs text-gray-400">文档分析</div>
          </div>
          <div className="bg-primary/50 rounded-lg p-3 text-center">
            <div className="text-accent text-xl mb-1">📊</div>
            <div className="text-xs text-gray-400">数据分析</div>
          </div>
        </div>
      </div>
    </aside>
  );
};
