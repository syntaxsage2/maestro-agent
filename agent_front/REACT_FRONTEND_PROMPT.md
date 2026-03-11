# React 前端开发 Prompt

## 项目概述

我需要你帮我创建一个 **React 前端应用**，用于连接我的 FastAPI 后端 AI Agent 系统。

**后端项目名称**: IntentRouter Pro  
**后端技术栈**: FastAPI + LangGraph + PostgreSQL + MCP  
**前端技术栈**: React + TypeScript + Vite（推荐）

---

## ? 核心功能需求

### 1. AI 对话界面（必需）

#### 1.1 基础聊天
- **消息输入框**：支持多行输入，Enter发送，Shift+Enter换行
- **消息展示区域**：
  - 用户消息：右对齐，蓝色背景
  - AI消息：左对齐，灰色背景
  - 时间戳显示
  - Markdown渲染（支持代码高亮）
- **流式响应**（重要）：
  - 使用 Server-Sent Events (SSE)
  - 实时显示AI思考过程
  - 显示当前执行的节点（如：路由中、RAG检索中、工具调用中）
  - 逐字显示AI回复（打字机效果）

#### 1.2 多模态支持（图片）
- **图片上传**：
  - 支持拖拽上传
  - 支持点击选择
  - 支持多张图片（最多5张）
  - 图片预览（可删除）
  - 支持的格式：jpg, png, gif, webp
  - 最大文件大小：10MB/图片
- **图片消息展示**：
  - 在消息中显示缩略图
  - 点击查看大图

#### 1.3 会话管理
- **会话列表侧边栏**（可折叠）：
  - 显示最近的会话列表
  - 每个会话显示：标题（第一条消息）、时间
  - 点击切换会话
  - 新建会话按钮
  - 删除会话按钮（带确认）
- **自动保存**：
  - 使用 `thread_id` 管理会话
  - localStorage 保存会话列表

---

### 2. 人机协同（HITL）界面（必需）

当AI需要执行高风险操作时，会暂停等待人工确认。

#### 2.1 中断检测
- 轮询 `/api/hitl/status/{thread_id}` 
- 检测到中断时显示确认对话框

#### 2.2 确认界面
- **显示待确认的操作**：
  - 工具名称（如：删除文件）
  - 参数详情（如：file_path: /data/test.txt）
  - 风险等级标识（?? 高风险）
- **操作按钮**：
  - ? 批准 (绿色)
  - ? 拒绝 (红色)
  - 可选：修改参数（高级功能）
- **确认后**：
  - 调用 `/api/hitl/approve` 或 `/api/hitl/reject`
  - 继续显示后续消息

---

### 3. 系统状态界面（可选但推荐）

#### 3.1 工具面板
- 显示可用工具列表（从 `/tools` 获取）
- 区分内置工具和MCP工具
- 显示工具描述

#### 3.2 会话详情面板
- 当前意图（intent）
- 路由决策（route）
- 已使用的工具
- 消息数量
- 检索文档数量

---

### 4. 设置页面（可选）

- 服务器地址配置
- 用户ID设置
- 主题切换（明暗模式）
- 清除所有会话

---

## ? UI/UX 设计要求

### 整体风格
- **现代化**：参考 ChatGPT、Claude 的界面风格
- **响应式**：支持桌面、平板、手机
- **流畅动画**：消息滑入、节点切换、加载指示器
- **易用性**：操作简单直观

### 布局建议

```
请参考前端静态页面样例.html文件
```

### 颜色方案建议

**明亮模式**:
- 背景：#ffffff
- 用户消息：#3b82f6（蓝色）
- AI消息：#f3f4f6（浅灰）
- 强调色：#10b981（绿色，用于成功）
- 警告色：#ef4444（红色，用于警告）

**暗黑模式**:
- 背景：#1f2937
- 用户消息：#3b82f6
- AI消息：#374151
- 强调色：#10b981
- 警告色：#ef4444

---

## ?? 技术栈建议

### 核心框架
- **React 18+** - 前端框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具（快速开发）

### UI 组件库（选一个）
- **shadcn/ui** + Tailwind CSS（推荐，现代化）
- **Ant Design**（完整组件库）
- **Material-UI**（Google风格）
- **Chakra UI**（简洁）

### 状态管理
- **Zustand**（推荐，轻量级）
- **Redux Toolkit**（复杂状态）
- **React Query** + Context API

### HTTP 客户端
- **axios** - HTTP请求
- **EventSource** - SSE流式响应（原生API）

### Markdown 渲染
- **react-markdown** - Markdown渲染
- **react-syntax-highlighter** - 代码高亮

### 其他工具
- **date-fns** 或 **dayjs** - 时间格式化
- **react-dropzone** - 文件上传
- **react-hot-toast** - 通知提示
- **zustand** - 状态管理

---

## ? API 集成说明

### 后端 API 基础信息

**Base URL**: `http://localhost:8000`

**完整API文档**: 参考 `API_DOCUMENTATION.md`

### 核心接口

#### 1. 普通对话
```typescript
POST /api/chat
Request: {
  message: string,
  thread_id?: string,
  user_id?: string
}
Response: {
  thread_id: string,
  message: string,
  intent?: string,
  route?: string,
  retrieved_docs_count: number
}
```

#### 2. 流式对话（SSE）
```typescript
POST /api/chat/stream
Request: 同上
Response: text/event-stream

事件类型：
- node_start: 节点开始
- node_end: 节点结束
- message: 消息生成
- token: 单个token
- done: 完成
- error: 错误
```

#### 3. 多模态对话
```typescript
POST /api/chat/multimodal
Content-Type: multipart/form-data
FormData:
- message: string
- files: File[]
- thread_id?: string
- user_id?: string
```

#### 4. 获取历史
```typescript
GET /api/history/{thread_id}
Response: {
  thread_id: string,
  messages: Array<{role: string, content: string}>
}
```

#### 5. HITL 状态
```typescript
GET /api/hitl/status/{thread_id}
Response: {
  is_interrupted: boolean,
  thread_id: string,
  interrupt_reason?: string,
  tool_calls?: Array<{name, args, risk_level}>
}
```

#### 6. HITL 批准/拒绝
```typescript
POST /api/hitl/approve/{thread_id}
POST /api/hitl/reject/{thread_id}
```

---

## ? 关键实现细节

### 1. SSE 流式响应实现

```typescript
// 使用 EventSource
const eventSource = new EventSource(`http://localhost:8000/api/chat/stream`, {
  // 注意：EventSource 默认不支持 POST
  // 需要使用 fetch-event-source 库
});

// 推荐使用 @microsoft/fetch-event-source
import { fetchEventSource } from '@microsoft/fetch-event-source';

await fetchEventSource('http://localhost:8000/api/chat/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: userMessage,
    thread_id: threadId
  }),
  onmessage(event) {
    const data = JSON.parse(event.data);
    switch(data.event) {
      case 'node_start':
        setCurrentNode(data.node);
        break;
      case 'message':
        setMessages(prev => [...prev, {
          role: data.role,
          content: data.content
        }]);
        break;
      case 'token':
        // 追加到当前消息
        appendToLastMessage(data.content);
        break;
      case 'done':
        setIsStreaming(false);
        break;
    }
  }
});
```

### 2. 轮询 HITL 状态

```typescript
// 发送消息后，开始轮询
const pollInterruptStatus = async (threadId: string) => {
  const interval = setInterval(async () => {
    const res = await axios.get(`/api/hitl/status/${threadId}`);
    if (res.data.is_interrupted) {
      clearInterval(interval);
      showConfirmDialog(res.data);
    }
  }, 1000); // 每秒检查一次
  
  // 30秒后停止轮询
  setTimeout(() => clearInterval(interval), 30000);
};
```

### 3. 图片上传处理

```typescript
const handleImageUpload = async (files: File[]) => {
  const formData = new FormData();
  formData.append('message', userMessage);
  
  files.forEach(file => {
    formData.append('files', file);
  });
  
  if (threadId) {
    formData.append('thread_id', threadId);
  }
  
  const response = await axios.post(
    '/api/chat/multimodal',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
  );
  
  return response.data;
};
```

### 4. 会话管理（localStorage）

```typescript
interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: number;
}

// 保存会话列表
const saveConversations = (conversations: Conversation[]) => {
  localStorage.setItem('conversations', JSON.stringify(conversations));
};

// 加载会话列表
const loadConversations = (): Conversation[] => {
  const data = localStorage.getItem('conversations');
  return data ? JSON.parse(data) : [];
};
```

---

## ? 项目结构建议

```
react-frontend/
├── public/
├── src/
│   ├── api/              # API 调用
│   │   ├── chat.ts
│   │   ├── history.ts
│   │   └── hitl.ts
│   ├── components/       # UI 组件
│   │   ├── Chat/
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageInput.tsx
│   │   │   ├── NodeStatus.tsx
│   │   │   └── ImageUpload.tsx
│   │   ├── Sidebar/
│   │   │   ├── ConversationList.tsx
│   │   │   └── NewChatButton.tsx
│   │   ├── HITL/
│   │   │   └── ConfirmDialog.tsx
│   │   └── Layout/
│   │       ├── Header.tsx
│   │       └── Layout.tsx
│   ├── hooks/            # 自定义 Hooks
│   │   ├── useChat.ts
│   │   ├── useSSE.ts
│   │   └── useHITL.ts
│   ├── store/            # 状态管理
│   │   └── chatStore.ts
│   ├── types/            # TypeScript 类型
│   │   └── api.ts
│   ├── utils/            # 工具函数
│   │   ├── markdown.ts
│   │   └── time.ts
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## ? 功能检查清单

### 必需功能
- [ ] 消息发送和显示
- [ ] 流式响应（SSE）
- [ ] 节点状态显示
- [ ] Markdown 渲染
- [ ] 代码高亮
- [ ] 会话管理（新建、切换、删除）
- [ ] 图片上传和预览
- [ ] HITL 确认对话框
- [ ] 响应式布局

### 推荐功能
- [ ] 明暗主题切换
- [ ] 消息时间戳
- [ ] 加载状态指示
- [ ] 错误提示
- [ ] 复制消息
- [ ] 重新生成回复
- [ ] 停止生成
- [ ] 工具调用历史查看

### 高级功能（可选）
- [ ] 语音输入
- [ ] 导出会话（JSON/Markdown）
- [ ] 搜索历史消息
- [ ] 快捷键支持
- [ ] 消息引用/回复
- [ ] 多语言支持
- [ ] PWA 支持

---

## ? UI 参考

可以参考以下应用的设计：
- **ChatGPT** - https://chat.openai.com
- **Claude** - https://claude.ai
- **Perplexity** - https://perplexity.ai
- **Poe** - https://poe.com

---

## ? 启动说明

### 开发环境
```bash
# 1. 创建项目
npm create vite@latest react-frontend -- --template react-ts

# 2. 安装依赖
cd react-frontend
npm install

# 3. 安装额外依赖
npm install axios zustand react-markdown react-syntax-highlighter
npm install @microsoft/fetch-event-source
npm install react-hot-toast react-dropzone
npm install date-fns

# 4. 启动开发服务器
npm run dev
```

### 生产构建
```bash
npm run build
```

---

## ?? 环境变量

创建 `.env` 文件：

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_MAX_IMAGE_SIZE=10485760
```

---

## ? 测试建议

### 功能测试场景

1. **基础对话**
   - 发送 "你好"
   - 发送 "Python asyncio 怎么用？"
   - 检查消息显示和格式

2. **流式响应**
   - 发送任意消息
   - 观察节点状态切换
   - 验证打字机效果

3. **多模态**
   - 上传图片，问 "这是什么？"
   - 上传多张图片
   - 测试图片预览和删除

4. **HITL**
   - 发送 "删除 /data/test.txt"
   - 验证确认对话框出现
   - 测试批准/拒绝功能

5. **会话管理**
   - 创建多个会话
   - 切换会话
   - 删除会话
   - 刷新页面后恢复

---

## ? 注意事项

1. **CORS**: 后端已配置允许 `http://localhost:3000` 和 `http://localhost:5173`
2. **SSE**: 使用 `@microsoft/fetch-event-source` 而不是原生 EventSource（支持POST）
3. **线程ID**: 首次对话不传 `thread_id`，后端会返回，之后使用同一个
4. **错误处理**: 所有API调用都要有错误处理和用户提示
5. **性能**: 消息列表使用虚拟滚动（如 `react-window`）处理大量消息

---

## ? 开发目标

最终交付一个：
- ? 功能完整的AI对话界面
- ? 美观现代的UI设计
- ? 流畅的用户体验
- ? 完善的错误处理
- ? 响应式布局
- ? TypeScript 类型安全
- ? 代码结构清晰

---

## ? 参考资料

- **后端API文档**: `API_DOCUMENTATION.md`
- **FastAPI Docs**: http://localhost:8000/docs
- **React文档**: https://react.dev
- **Vite文档**: https://vitejs.dev
- **Tailwind CSS**: https://tailwindcss.com
- **shadcn/ui**: https://ui.shadcn.com

---

## ? 常见问题

### Q: SSE 连接失败？
A: 检查CORS配置，确保使用 `@microsoft/fetch-event-source`

### Q: 图片上传失败？
A: 检查文件大小（最大10MB），确保使用 `multipart/form-data`

### Q: HITL 检测不到中断？
A: 确保轮询间隔合理（1秒），检查后端日志

### Q: 会话切换后消息丢失？
A: 调用 `/api/history/{thread_id}` 加载历史消息

---

好的，以上就是完整的需求。请帮我创建这个 React 前端应用！

