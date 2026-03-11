import { Menu, Plus } from 'lucide-react';
import { useChatStore } from '../../store/chatStore';
import { UserMenu } from './UserMenu';
import type { User } from '../../api/auth';

interface HeaderProps {
  user?: User;
  onLogout?: () => void;
}

export const Header = ({ user, onLogout }: HeaderProps) => {
  const { toggleSidebar, addConversation } = useChatStore();

  const handleNewChat = () => {
    const newConvId = `thread_${Date.now()}`;
    addConversation({
      id: newConvId,
      title: '新对话',
      messages: [],
      lastUpdated: Date.now(),
    });
  };

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-gray-800 bg-primary/50 backdrop-blur-sm">
      <div className="flex items-center gap-4">
        <button
          onClick={toggleSidebar}
          className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
          aria-label="切换侧边栏"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-accent rounded-xl flex items-center justify-center">
            <span className="text-xl">🤖</span>
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-accent-light to-blue-400 text-transparent bg-clip-text">
              AI Agent
            </h1>
            <p className="text-xs text-gray-400">智能助手</p>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={handleNewChat}
          className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent-light text-white rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span className="hidden sm:inline">新对话</span>
        </button>

        {user && onLogout && <UserMenu user={user} onLogout={onLogout} />}
      </div>
    </header>
  );
};
