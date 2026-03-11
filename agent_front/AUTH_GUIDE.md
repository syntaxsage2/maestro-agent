# 用户认证系统使用指南

## 概述

IntentRouter Pro 现在支持用户认证系统，允许：
- 用户注册和登录
- 基于 JWT 的令牌认证
- 用户画像与长期记忆关联
- 多用户隔离

## 目录

1. [快速开始](#快速开始)
2. [API 端点](#api-端点)
3. [前端集成](#前端集成)
4. [数据库配置](#数据库配置)
5. [安全配置](#安全配置)

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

新增的依赖包括：
- `python-jose[cryptography]` - JWT 处理
- `passlib[bcrypt]` - 密码加密
- `python-multipart` - 表单数据处理

### 2. 初始化数据库

运行数据库初始化脚本来创建用户表：

```bash
psql -U your_user -d your_database -f ops/init_db.sql
```

这将创建：
- `users` 表 - 存储用户信息
- 更新 `long_term_memory` 表 - 与用户表建立外键关系
- 更新 `tasks` 表 - 与用户表建立外键关系

### 3. 配置安全密钥

?? **重要**: 在生产环境中，请修改 `intentrouter/utils/auth_utils.py` 中的 `SECRET_KEY`：

```python
# 从环境变量读取
import os
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
```

建议生成一个强随机密钥：

```bash
openssl rand -hex 32
```

### 4. 启动 API

```bash
uvicorn intentrouter.api.main:app --reload
```

---

## API 端点

### 认证端点

所有认证端点都在 `/api/auth` 前缀下。

#### 1. 用户注册

**POST** `/api/auth/register`

注册新用户并返回 JWT token。

**请求体：**
```json
{
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "password": "password123",
  "full_name": "张三"
}
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "full_name": "张三",
    "avatar_url": null,
    "is_active": true,
    "is_superuser": false,
    "created_at": "2025-10-28T10:00:00",
    "updated_at": "2025-10-28T10:00:00"
  }
}
```

**示例：**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "password": "password123",
    "full_name": "张三"
  }'
```

#### 2. 用户登录

**POST** `/api/auth/login`

使用用户名和密码登录，返回 JWT token。

**请求体：**
```json
{
  "username": "zhangsan",
  "password": "password123"
}
```

**响应：**（与注册相同）

**示例：**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "zhangsan",
    "password": "password123"
  }'
```

#### 3. 获取当前用户信息

**GET** `/api/auth/me`

获取当前登录用户的信息。

**请求头：**
```
Authorization: Bearer <your_token>
```

**响应：**
```json
{
  "id": 1,
  "username": "zhangsan",
  "email": "zhangsan@example.com",
  "full_name": "张三",
  "avatar_url": null,
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-10-28T10:00:00",
  "updated_at": "2025-10-28T10:00:00"
}
```

**示例：**
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 4. 更新用户信息

**PUT** `/api/auth/me`

更新当前用户的个人信息。

**请求头：**
```
Authorization: Bearer <your_token>
```

**请求体：**
```json
{
  "full_name": "张三丰",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

**响应：**（返回更新后的用户信息）

**示例：**
```bash
curl -X PUT http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "张三丰",
    "avatar_url": "https://example.com/avatar.jpg"
  }'
```

#### 5. 获取用户画像

**GET** `/api/auth/profile`

获取用户画像，包含用户信息和长期记忆。

**请求头：**
```
Authorization: Bearer <your_token>
```

**响应：**
```json
{
  "user": {
    "id": 1,
    "username": "zhangsan",
    "email": "zhangsan@example.com",
    "full_name": "张三"
  },
  "facts": [
    {
      "content": "是一名 Python 开发者",
      "importance": 0.8
    }
  ],
  "preferences": [
    {
      "content": "喜欢使用 LangChain",
      "importance": 0.7
    }
  ],
  "skills": [
    {
      "content": "擅长 FastAPI 开发",
      "importance": 0.9
    }
  ],
  "total_memories": 3
}
```

**示例：**
```bash
curl -X GET http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 聊天端点（需要认证）

所有聊天端点现在都需要 JWT token 认证。

#### 1. 标准聊天

**POST** `/api/chat`

**请求头：**
```
Authorization: Bearer <your_token>
```

**请求体：**
```json
{
  "message": "你好，介绍一下 LangGraph",
  "thread_id": "optional-thread-id"
}
```

**注意：** 
- `user_id` 字段已被移除，系统会自动使用当前登录用户的 ID
- `thread_id` 是可选的，不提供则自动生成

**示例：**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好，介绍一下 LangGraph"
  }'
```

#### 2. 流式聊天

**POST** `/api/chat/stream`

**请求头：**
```
Authorization: Bearer <your_token>
```

**请求体：**（与标准聊天相同）

**示例：**
```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "你好"
  }'
```

#### 3. 多模态聊天

**POST** `/api/chat/multimodal`

**请求头：**
```
Authorization: Bearer <your_token>
```

**请求体：**（multipart/form-data）
- `message`: 文本消息
- `files`: 图片文件（可多个）
- `thread_id`: 可选

**示例：**
```bash
curl -X POST http://localhost:8000/api/chat/multimodal \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "message=这张图片里有什么？" \
  -F "files=@image.jpg"
```

---

## 前端集成

### React/JavaScript 示例

#### 1. 用户注册

```javascript
async function register(username, email, password, fullName) {
  const response = await fetch('http://localhost:8000/api/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username,
      email,
      password,
      full_name: fullName
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }

  const data = await response.json();
  
  // 保存 token 到 localStorage
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  
  return data;
}
```

#### 2. 用户登录

```javascript
async function login(username, password) {
  const response = await fetch('http://localhost:8000/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '登录失败');
  }

  const data = await response.json();
  
  // 保存 token
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));
  
  return data;
}
```

#### 3. 发送聊天消息（带认证）

```javascript
async function sendMessage(message, threadId = null) {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    throw new Error('请先登录');
  }

  const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      message,
      thread_id: threadId
    })
  });

  if (response.status === 401) {
    // Token 过期或无效，重新登录
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    throw new Error('登录已过期，请重新登录');
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || '请求失败');
  }

  return await response.json();
}
```

#### 4. 获取用户画像

```javascript
async function getUserProfile() {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    throw new Error('请先登录');
  }

  const response = await fetch('http://localhost:8000/api/auth/profile', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error('获取用户画像失败');
  }

  return await response.json();
}
```

#### 5. 完整的 React Hook 示例

```javascript
import { useState, useEffect } from 'react';

function useAuth() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // 从 localStorage 恢复登录状态
    const savedToken = localStorage.getItem('access_token');
    const savedUser = localStorage.getItem('user');
    
    if (savedToken && savedUser) {
      setToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
    
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    const response = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail);
    }

    const data = await response.json();
    
    setToken(data.access_token);
    setUser(data.user);
    
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  };

  return {
    user,
    token,
    loading,
    isAuthenticated: !!token,
    login,
    logout
  };
}

// 使用示例
function App() {
  const { user, isAuthenticated, login, logout } = useAuth();

  if (!isAuthenticated) {
    return <LoginPage onLogin={login} />;
  }

  return (
    <div>
      <h1>欢迎, {user.full_name || user.username}!</h1>
      <button onClick={logout}>登出</button>
      <ChatInterface token={token} />
    </div>
  );
}
```

---

## 数据库配置

### 用户表结构

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT TRUE,
    is_superuser BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 长期记忆与用户关联

长期记忆现在使用 `user_id` (INTEGER) 直接关联到 `users` 表：

```sql
CREATE TABLE long_term_memory (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    memory_type VARCHAR(50),
    content TEXT NOT NULL,
    importance FLOAT DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT NOW(),
    accessed_at TIMESTAMP DEFAULT NOW(),
    access_count INT DEFAULT 0
);
```

---

## 安全配置

### JWT Token 配置

在 `intentrouter/utils/auth_utils.py` 中配置：

```python
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 天
```

### 建议的安全实践

1. **生产环境必须更改密钥**
   ```python
   import os
   SECRET_KEY = os.getenv("JWT_SECRET_KEY")
   ```

2. **设置合理的 Token 过期时间**
   ```python
   ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 天（推荐）
   ```

3. **HTTPS 部署**
   - 生产环境必须使用 HTTPS
   - 防止 Token 在传输中被窃取

4. **CORS 配置**
   - 在 `main.py` 中配置允许的前端域名
   - 不要在生产环境使用 `allow_origins=["*"]`

5. **密码强度要求**
   - 当前最低要求：6 位
   - 建议在前端添加更严格的验证

---

## 常见问题

### Q: Token 过期后如何处理？

A: 前端需要检测 401 状态码，并引导用户重新登录：

```javascript
if (response.status === 401) {
  // 清除本地存储
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  // 跳转到登录页
  window.location.href = '/login';
}
```

### Q: 如何实现 Token 刷新？

A: 当前实现使用长期 Token（7天）。如需实现 Refresh Token 机制，需要：
1. 添加 `refresh_token` 表
2. 创建 `/auth/refresh` 端点
3. 前端在 Token 即将过期时自动刷新

### Q: 如何实现用户注销？

A: JWT 是无状态的，不需要服务器端注销。前端只需删除本地存储的 Token：

```javascript
function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  window.location.href = '/login';
}
```

### Q: 如何支持第三方登录（OAuth）？

A: 需要额外集成 OAuth 库：
- Google: `authlib` + Google OAuth 配置
- GitHub: `authlib` + GitHub OAuth 配置
- 微信: 使用微信开放平台 SDK

### Q: 数据库迁移时如何处理现有数据？

A: 如果已有 `long_term_memory` 数据使用字符串 `user_id`，需要：

1. 创建迁移脚本：
```sql
-- 1. 为现有数据创建默认用户
INSERT INTO users (username, email, hashed_password, full_name)
VALUES ('legacy_user', 'legacy@example.com', 'hashed_password_here', 'Legacy User')
ON CONFLICT DO NOTHING;

-- 2. 备份并清空 long_term_memory（如果数据重要，先导出）
-- 或者创建映射关系将旧的 user_id 转换为新的整数 ID
```

---

## 下一步

- [ ] 添加邮箱验证
- [ ] 实现密码重置功能
- [ ] 添加 Refresh Token 机制
- [ ] 支持第三方登录（OAuth）
- [ ] 添加用户权限管理
- [ ] 实现 API 速率限制（按用户）

---

## 支持

如有问题，请查看：
- API 文档: http://localhost:8000/docs
- 项目 README: ../README.md

