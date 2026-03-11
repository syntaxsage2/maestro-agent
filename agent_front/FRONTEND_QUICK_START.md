# 前端开发快速开始

## ? 给 AI 的 Prompt（精简版）

```
我需要你创建一个 React + TypeScript 的 AI 对话应用前端。

后端 API: http://localhost:8000
完整文档: 见 REACT_FRONTEND_PROMPT.md

核心功能：
1. AI 对话界面（支持流式响应 SSE）
2. 图片上传（多模态）
3. 会话管理（侧边栏）
4. 人工确认界面（HITL）

技术栈：
- React 18 + TypeScript + Vite
- Tailwind CSS + shadcn/ui
- Zustand（状态）
- @microsoft/fetch-event-source（SSE）
- react-markdown（Markdown渲染）

参考设计：ChatGPT 风格

请帮我生成完整的项目代码。
```

---

## ? 快速创建项目

### 方式1：使用 Vite（推荐）

```bash
# 创建项目
npm create vite@latest intentrouter-chat -- --template react-ts
cd intentrouter-chat

# 安装核心依赖
npm install

# 安装额外依赖
npm install axios zustand
npm install @microsoft/fetch-event-source
npm install react-markdown remark-gfm
npm install react-syntax-highlighter
npm install @types/react-syntax-highlighter -D
npm install react-hot-toast
npm install react-dropzone
npm install date-fns
npm install lucide-react  # 图标

# Tailwind CSS
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 启动开发服务器
npm run dev
```

### 方式2：使用 Next.js

```bash
npx create-next-app@latest intentrouter-chat --typescript --tailwind --app
cd intentrouter-chat
npm install axios zustand @microsoft/fetch-event-source react-markdown
npm run dev
```

---

## ? package.json 示例

```json
{
  "name": "intentrouter-chat",
  "private": true,
  "version": "0.0.1",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "zustand": "^4.4.0",
    "@microsoft/fetch-event-source": "^2.0.1",
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0",
    "react-syntax-highlighter": "^15.5.0",
    "react-hot-toast": "^2.4.1",
    "react-dropzone": "^14.2.3",
    "date-fns": "^3.0.0",
    "lucide-react": "^0.300.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/react-syntax-highlighter": "^15.5.0",
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "@vitejs/plugin-react": "^4.2.0",
    "autoprefixer": "^10.4.0",
    "eslint": "^8.55.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.2.0",
    "vite": "^5.0.0"
  }
}
```

---

## ? Tailwind 配置

`tailwind.config.js`:

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3b82f6',
          dark: '#2563eb',
        },
        danger: {
          DEFAULT: '#ef4444',
          dark: '#dc2626',
        }
      }
    },
  },
  plugins: [],
  darkMode: 'class', // 支持暗黑模式
}
```

`src/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body {
    @apply bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100;
  }
}
```

---

## ? 项目结构

```
src/
├── api/
│   ├── client.ts          # axios 实例
│   ├── chat.ts            # 对话 API
│   ├── history.ts         # 历史 API
│   └── hitl.ts            # HITL API
├── components/
│   ├── Chat/
│   │   ├── ChatContainer.tsx
│   │   ├── MessageList.tsx
│   │   ├── MessageItem.tsx
│   │   ├── MessageInput.tsx
│   │   ├── NodeStatus.tsx
│   │   └── ImageUpload.tsx
│   ├── Sidebar/
│   │   ├── Sidebar.tsx
│   │   ├── ConversationList.tsx
│   │   └── ConversationItem.tsx
│   ├── HITL/
│   │   └── ConfirmDialog.tsx
│   ├── Layout/
│   │   ├── Layout.tsx
│   │   └── Header.tsx
│   └── common/
│       ├── Button.tsx
│       ├── Input.tsx
│       └── Modal.tsx
├── hooks/
│   ├── useChat.ts         # 对话逻辑
│   ├── useSSE.ts          # SSE 流式
│   ├── useHITL.ts         # HITL 逻辑
│   └── useConversations.ts
├── store/
│   └── chatStore.ts       # Zustand store
├── types/
│   └── api.ts             # TypeScript 类型
├── utils/
│   ├── markdown.tsx       # Markdown 组件
│   └── time.ts            # 时间格式化
├── App.tsx
└── main.tsx
```

---

## ? 核心代码示例

### 1. API Client

`src/api/client.ts`:

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);
```

### 2. TypeScript 类型

`src/types/api.ts`:

```typescript
export interface ChatRequest {
  message: string;
  thread_id?: string;
  user_id?: string;
  stream?: boolean;
}

export interface ChatResponse {
  thread_id: string;
  message: string;
  intent?: string;
  route?: string;
  retrieved_docs_count: number;
}

export interface Message {
  role: 'human' | 'ai';
  content: string;
  timestamp?: number;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  lastUpdated: number;
}

export interface SSEEvent {
  event: 'node_start' | 'node_end' | 'message' | 'token' | 'done' | 'error';
  node?: string;
  content?: string;
  role?: string;
}

export interface HITLStatus {
  is_interrupted: boolean;
  thread_id: string;
  next_node?: string;
  interrupt_reason?: string;
  tool_calls?: ToolCall[];
}

export interface ToolCall {
  name: string;
  args: Record<string, any>;
  risk_level?: string;
}
```

### 3. Zustand Store

`src/store/chatStore.ts`:

```typescript
import { create } from 'zustand';
import { Message, Conversation } from '../types/api';

interface ChatStore {
  conversations: Conversation[];
  currentConversationId: string | null;
  isStreaming: boolean;
  currentNode: string | null;
  
  // Actions
  addConversation: (conversation: Conversation) => void;
  setCurrentConversation: (id: string) => void;
  addMessage: (conversationId: string, message: Message) => void;
  setIsStreaming: (isStreaming: boolean) => void;
  setCurrentNode: (node: string | null) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  conversations: [],
  currentConversationId: null,
  isStreaming: false,
  currentNode: null,
  
  addConversation: (conversation) =>
    set((state) => ({
      conversations: [...state.conversations, conversation],
      currentConversationId: conversation.id,
    })),
  
  setCurrentConversation: (id) =>
    set({ currentConversationId: id }),
  
  addMessage: (conversationId, message) =>
    set((state) => ({
      conversations: state.conversations.map((conv) =>
        conv.id === conversationId
          ? { ...conv, messages: [...conv.messages, message] }
          : conv
      ),
    })),
  
  setIsStreaming: (isStreaming) => set({ isStreaming }),
  
  setCurrentNode: (node) => set({ currentNode: node }),
}));
```

### 4. SSE Hook

`src/hooks/useSSE.ts`:

```typescript
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { SSEEvent } from '../types/api';

export const useSSE = () => {
  const streamChat = async (
    message: string,
    threadId: string | undefined,
    onEvent: (event: SSEEvent) => void
  ) => {
    const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    
    await fetchEventSource(`${API_BASE}/api/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        thread_id: threadId,
      }),
      onmessage(event) {
        const data: SSEEvent = JSON.parse(event.data);
        onEvent(data);
      },
      onerror(error) {
        console.error('SSE Error:', error);
        throw error;
      },
    });
  };
  
  return { streamChat };
};
```

---

## ? UI 组件示例

### MessageItem Component

```tsx
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface MessageItemProps {
  role: 'human' | 'ai';
  content: string;
  timestamp?: number;
}

export const MessageItem = ({ role, content, timestamp }: MessageItemProps) => {
  const isUser = role === 'human';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[70%] rounded-lg px-4 py-2 ${
          isUser
            ? 'bg-blue-500 text-white'
            : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
        }`}
      >
        <ReactMarkdown
          components={{
            code({ node, inline, className, children, ...props }) {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <SyntaxHighlighter
                  style={oneDark}
                  language={match[1]}
                  PreTag="div"
                  {...props}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
          }}
        >
          {content}
        </ReactMarkdown>
      </div>
    </div>
  );
};
```

---

## ? 性能优化建议

1. **虚拟滚动**：消息列表使用 `react-window`
2. **图片懒加载**：使用 `react-lazy-load-image-component`
3. **防抖输入**：输入框使用 `lodash.debounce`
4. **Memo优化**：使用 `React.memo` 包装组件
5. **代码分割**：使用 `React.lazy` + `Suspense`

---

## ? 调试技巧

```typescript
// 在开发环境打印API请求
apiClient.interceptors.request.use((config) => {
  console.log('API Request:', config.method?.toUpperCase(), config.url);
  return config;
});

// SSE 调试
onEvent: (event) => {
  console.log('SSE Event:', event);
  // 处理事件...
}
```

---

## ? 学习资源

- **React**: https://react.dev/learn
- **TypeScript**: https://www.typescriptlang.org/docs/
- **Tailwind**: https://tailwindcss.com/docs
- **Zustand**: https://docs.pmnd.rs/zustand
- **Vite**: https://vitejs.dev/guide/

---

## ? 检查清单

创建项目后检查：

- [ ] `npm run dev` 启动成功
- [ ] 可以访问 http://localhost:5173
- [ ] 可以连接后端 API
- [ ] 消息发送和接收正常
- [ ] 流式响应正常
- [ ] 图片上传正常
- [ ] 会话管理正常
- [ ] 暗黑模式切换正常

---

准备好了吗？开始创建你的 AI 对话前端吧！?

