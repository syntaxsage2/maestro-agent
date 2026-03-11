# IntentRouter Chat - AI Agent 智能助手前端

这是一个基于 React + TypeScript + Vite 构建的现代化 AI 对话应用，用于连接 IntentRouter Pro FastAPI 后端系统。

## ✨ 功能特性

### 核心功能
- ✅ **AI 对话界面** - 支持流式响应（SSE）
- ✅ **多模态支持** - 图片上传和分析
- ✅ **会话管理** - 创建、切换、删除对话
- ✅ **HITL（人机协同）** - 高风险操作人工确认
- ✅ **节点状态显示** - 实时显示 AI 执行进度
- ✅ **Markdown 渲染** - 支持代码高亮
- ✅ **响应式布局** - 支持桌面和移动设备

### 技术栈
- **React 18** - 前端框架
- **TypeScript** - 类型安全
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **Zustand** - 状态管理
- **@microsoft/fetch-event-source** - SSE 流式响应
- **react-markdown** - Markdown 渲染
- **react-syntax-highlighter** - 代码高亮
- **react-hot-toast** - 通知提示
- **react-dropzone** - 文件上传
- **lucide-react** - 图标库

## 🚀 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env`，并根据需要修改：

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_MAX_IMAGE_SIZE=10485760
VITE_MAX_IMAGES=5
```

### 3. 启动开发服务器

```bash
npm run dev
```

应用将在 http://localhost:5173 启动

### 4. 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist` 目录

## 📁 项目结构

```
src/
├── api/              # API 调用
│   ├── client.ts     # axios 客户端
│   ├── chat.ts       # 聊天 API
│   ├── history.ts    # 历史 API
│   ├── hitl.ts       # HITL API
│   └── system.ts     # 系统 API
├── components/       # UI 组件
│   ├── Chat/
│   │   ├── ChatContainer.tsx
│   │   ├── MessageList.tsx
│   │   ├── MessageItem.tsx
│   │   ├── MessageInput.tsx
│   │   ├── NodeStatus.tsx
│   │   └── ImageUpload.tsx
│   ├── Sidebar/
│   │   └── Sidebar.tsx
│   ├── HITL/
│   │   └── ConfirmDialog.tsx
│   └── Layout/
│       ├── Header.tsx
│       └── Layout.tsx
├── hooks/            # 自定义 Hooks
│   ├── useChat.ts
│   ├── useSSE.ts
│   └── useHITL.ts
├── store/            # 状态管理
│   └── chatStore.ts
├── types/            # TypeScript 类型
│   └── api.ts
├── utils/            # 工具函数
│   ├── time.ts
│   └── storage.ts
├── App.tsx
├── main.tsx
└── index.css
```

## 🎯 使用指南

### 基础对话
1. 点击右上角"新对话"创建会话
2. 在输入框输入消息
3. 按 Enter 发送，Shift+Enter 换行
4. AI 将流式返回回复

### 图片上传
1. 点击输入框左侧的图片图标
2. 拖拽图片或点击选择
3. 最多支持 5 张图片，每张最大 10MB
4. 输入问题并发送

### 人工确认（HITL）
1. 当 AI 需要执行高风险操作时，会弹出确认对话框
2. 查看操作详情和风险等级
3. 点击"批准"或"拒绝"
4. 可选填写原因

### 会话管理
- 点击左侧会话列表切换对话
- 点击删除图标删除对话
- 会话自动保存到 localStorage

## 🔌 API 集成

后端 API 地址：http://localhost:8000

主要接口：
- `POST /api/chat` - 普通对话
- `POST /api/chat/stream` - 流式对话（SSE）
- `POST /api/chat/multimodal` - 多模态对话
- `GET /api/history/{thread_id}` - 获取历史
- `GET /api/hitl/status/{thread_id}` - HITL 状态
- `POST /api/hitl/approve/{thread_id}` - 批准操作
- `POST /api/hitl/reject/{thread_id}` - 拒绝操作

详细 API 文档请参考：[API_DOCUMENTATION.md](../API_DOCUMENTATION.md)

## 🎨 UI 设计

界面采用深色主题，参考了 ChatGPT 和 Claude 的现代化设计：
- 渐变背景
- 毛玻璃效果
- 平滑动画
- 响应式布局

主要颜色：
- 主色调：#0f172a（深蓝）
- 强调色：#14b8a6（青绿）
- 用户消息：#3b82f6（蓝色）
- AI 消息：#334155（灰色）

## 🛠️ 开发建议

### 调试
- 打开浏览器控制台查看日志
- SSE 事件会在控制台输出
- API 请求和响应会记录

### 性能优化
- 消息列表使用虚拟滚动（可考虑 react-window）
- 图片懒加载
- 代码分割

### 扩展功能
- [ ] 语音输入
- [ ] 导出对话
- [ ] 搜索历史消息
- [ ] 快捷键支持
- [ ] 主题切换

## 📝 注意事项

1. **后端服务** - 确保 FastAPI 后端已启动在 http://localhost:8000
2. **CORS 配置** - 后端已配置允许 localhost:5173
3. **线程 ID** - 首次对话不传 thread_id，后端会返回
4. **SSE 连接** - 使用 @microsoft/fetch-event-source 支持 POST
5. **图片上传** - 使用 multipart/form-data 格式

## 🐛 常见问题

### Q: API 连接失败？
A: 检查后端服务是否启动，确认 VITE_API_BASE_URL 配置正确

### Q: SSE 流式响应不工作？
A: 检查浏览器控制台错误，确认后端 CORS 配置

### Q: 图片上传失败？
A: 检查图片大小（最大 10MB）和格式（jpg/png/gif/webp）

### Q: 会话数据丢失？
A: 会话保存在 localStorage，清除浏览器数据会丢失

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题，请联系开发团队。
