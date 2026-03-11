import { useState, useRef, useEffect } from 'react';
import { LogOut, User, Moon, Sun, ChevronDown } from 'lucide-react';
import { useThemeStore } from '../../store/themeStore';
import type { User as UserType } from '../../api/auth';

interface UserMenuProps {
  user: UserType;
  onLogout: () => void;
}

export const UserMenu = ({ user, onLogout }: UserMenuProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const { theme, toggleTheme } = useThemeStore();

  // 点击外部关闭菜单
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleToggleTheme = () => {
    toggleTheme();
    // 可以保持菜单打开状态，让用户看到切换效果
  };

  const handleLogout = () => {
    setIsOpen(false);
    onLogout();
  };

  // 获取用户显示名称
  const displayName = user.full_name || user.username;

  // 获取用户头像首字母
  const avatarLetter = displayName.charAt(0).toUpperCase();

  return (
    <div className="relative" ref={menuRef}>
      {/* 用户按钮 */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 hover:bg-gray-800 rounded-lg transition-colors group"
        aria-label="用户菜单"
      >
        {/* 头像 */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-accent to-blue-500 flex items-center justify-center text-white font-semibold text-sm">
          {user.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={displayName}
              className="w-full h-full rounded-full object-cover"
            />
          ) : (
            avatarLetter
          )}
        </div>

        {/* 用户名 */}
        <span className="text-sm font-medium text-gray-300 group-hover:text-white hidden md:block">
          {displayName}
        </span>

        {/* 下拉箭头 */}
        <ChevronDown
          className={`w-4 h-4 text-gray-400 transition-transform hidden md:block ${
            isOpen ? 'rotate-180' : ''
          }`}
        />
      </button>

      {/* 下拉菜单 */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-64 bg-gray-800 border border-gray-700 rounded-xl shadow-xl overflow-hidden z-50 animate-in fade-in slide-in-from-top-2 duration-200">
          {/* 用户信息 */}
          <div className="px-4 py-3 border-b border-gray-700 bg-gray-900/50">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-accent to-blue-500 flex items-center justify-center text-white font-semibold">
                {user.avatar_url ? (
                  <img
                    src={user.avatar_url}
                    alt={displayName}
                    className="w-full h-full rounded-full object-cover"
                  />
                ) : (
                  avatarLetter
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{displayName}</p>
                <p className="text-xs text-gray-400 truncate">{user.email}</p>
              </div>
            </div>
          </div>

          {/* 菜单项 */}
          <div className="py-2">
            {/* 个人信息 */}
            <button
              className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-300 hover:bg-gray-700/50 transition-colors"
              onClick={() => {
                setIsOpen(false);
                // TODO: 跳转到个人信息页面
              }}
            >
              <User className="w-4 h-4" />
              <span>个人信息</span>
            </button>

            {/* 主题切换 */}
            <button
              className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-300 hover:bg-gray-700/50 transition-colors"
              onClick={handleToggleTheme}
            >
              {theme === 'dark' ? (
                <>
                  <Sun className="w-4 h-4" />
                  <span>切换到亮色</span>
                </>
              ) : (
                <>
                  <Moon className="w-4 h-4" />
                  <span>切换到暗色</span>
                </>
              )}
            </button>
          </div>

          {/* 登出 */}
          <div className="border-t border-gray-700 py-2">
            <button
              className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-400 hover:bg-red-500/10 transition-colors"
              onClick={handleLogout}
            >
              <LogOut className="w-4 h-4" />
              <span>退出登录</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
