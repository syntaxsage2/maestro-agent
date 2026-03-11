import { useState } from 'react';
import { LogIn, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import type { LoginRequest } from '../../api/auth';

interface LoginPageProps {
  onLogin: (credentials: LoginRequest) => Promise<void>;
  onSwitchToRegister: () => void;
}

export const LoginPage = ({ onLogin, onSwitchToRegister }: LoginPageProps) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!username.trim() || !password.trim()) {
      toast.error('请输入用户名和密码');
      return;
    }

    setLoading(true);

    try {
      await onLogin({ username, password });
      toast.success('登录成功！');
    } catch (error) {
      const message = error instanceof Error ? error.message : '登录失败';
      toast.error(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-primary to-gray-900 p-4">
      <div className="max-w-md w-full">
        {/* Logo 和标题 */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-accent rounded-2xl mb-4">
            <span className="text-3xl">🤖</span>
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-accent-light to-blue-400 text-transparent bg-clip-text">
            AI Agent
          </h1>
          <p className="text-gray-400 mt-2">欢迎回来，请登录您的账号</p>
        </div>

        {/* 登录表单 */}
        <div className="bg-gray-800/50 backdrop-blur-sm rounded-2xl border border-gray-700 p-8 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 用户名 */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-300 mb-2">
                用户名
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 bg-gray-900/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-all"
                placeholder="请输入用户名"
                disabled={loading}
                autoComplete="username"
              />
            </div>

            {/* 密码 */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                密码
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 bg-gray-900/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent transition-all"
                placeholder="请输入密码"
                disabled={loading}
                autoComplete="current-password"
              />
            </div>

            {/* 登录按钮 */}
            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-accent hover:bg-accent-light text-white font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>登录中...</span>
                </>
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  <span>登录</span>
                </>
              )}
            </button>
          </form>

          {/* 切换到注册 */}
          <div className="mt-6 text-center">
            <p className="text-gray-400 text-sm">
              还没有账号？
              <button
                onClick={onSwitchToRegister}
                className="ml-2 text-accent hover:text-accent-light transition-colors font-medium"
                disabled={loading}
              >
                立即注册
              </button>
            </p>
          </div>
        </div>

        {/* 底部提示 */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>登录即表示您同意我们的服务条款和隐私政策</p>
        </div>
      </div>
    </div>
  );
};
