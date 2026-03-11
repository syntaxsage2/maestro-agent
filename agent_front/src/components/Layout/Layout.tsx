import { ReactNode } from 'react';
import { Header } from './Header';
import { Sidebar } from '../Sidebar/Sidebar';
import { useChatStore } from '../../store/chatStore';
import type { User } from '../../api/auth';

interface LayoutProps {
  children: ReactNode;
  user?: User;
  onLogout?: () => void;
}

export const Layout = ({ children, user, onLogout }: LayoutProps) => {
  const { showSidebar } = useChatStore();

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <Header user={user} onLogout={onLogout} />

      <div className="flex flex-1 overflow-hidden">
        {showSidebar && <Sidebar />}

        <main className="flex-1 flex flex-col overflow-hidden">
          {children}
        </main>
      </div>
    </div>
  );
};
