import { useEffect, useState } from 'react';
import { Toaster } from 'react-hot-toast';
import { Layout } from './components/Layout/Layout';
import { ChatContainer } from './components/Chat/ChatContainer';
import { LoginPage } from './components/Auth/LoginPage';
import { RegisterPage } from './components/Auth/RegisterPage';
import { useChatStore } from './store/chatStore';
import { useAuth } from './hooks/useAuth';
import type { LoginRequest, RegisterRequest } from './api/auth';

type AuthView = 'login' | 'register';

function App() {
  const { initStore } = useChatStore();
  const { user, loading, isAuthenticated, login, register, logout } = useAuth();
  const [authView, setAuthView] = useState<AuthView>('login');

  useEffect(() => {
    // 初始化 Store（从 localStorage 加载数据）
    initStore();
  }, [initStore]);

  // 处理登录
  const handleLogin = async (credentials: LoginRequest) => {
    await login(credentials);
  };

  // 处理注册
  const handleRegister = async (data: RegisterRequest) => {
    await register(data);
  };

  // 处理退出
  const handleLogout = () => {
    logout();
  };

  // 显示加载状态
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-primary to-gray-900">
        <div className="text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-accent rounded-2xl mb-4 animate-pulse">
            <span className="text-3xl">🤖</span>
          </div>
          <p className="text-gray-400">加载中...</p>
        </div>
      </div>
    );
  }

  // 未登录时显示认证页面
  if (!isAuthenticated) {
    if (authView === 'login') {
      return (
        <>
          <LoginPage
            onLogin={handleLogin}
            onSwitchToRegister={() => setAuthView('register')}
          />
          <Toaster position="top-right" />
        </>
      );
    } else {
      return (
        <>
          <RegisterPage
            onRegister={handleRegister}
            onSwitchToLogin={() => setAuthView('login')}
          />
          <Toaster position="top-right" />
        </>
      );
    }
  }

  // 已登录时显示主应用
  return (
    <>
      <Layout user={user || undefined} onLogout={handleLogout}>
        <ChatContainer />
      </Layout>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: '#1e293b',
            color: '#f1f5f9',
            border: '1px solid #334155',
          },
          success: {
            iconTheme: {
              primary: '#14b8a6',
              secondary: '#f1f5f9',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#f1f5f9',
            },
          },
        }}
      />
    </>
  );
}

export default App;
