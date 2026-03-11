-- IntentRouter Pro 数据库初始化脚本

-- LangGraph Checkpointer 会自动创建 checkpoints 表
-- 这里只需要创建额外的业务表

-- 创建用户表
CREATE TABLE IF NOT EXISTS users (
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

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 创建长期记忆表（Step 5 会用到）
CREATE TABLE IF NOT EXISTS long_term_memory (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    memory_type VARCHAR(50),              -- fact | preference | skill
    content TEXT NOT NULL,
    importance FLOAT DEFAULT 0.5,
    created_at TIMESTAMP DEFAULT NOW(),
    accessed_at TIMESTAMP DEFAULT NOW(),
    access_count INT DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_ltm_user_id ON long_term_memory(user_id);

-- 创建任务记录表
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id VARCHAR(255) NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    intent VARCHAR(50),
    status VARCHAR(50),                   -- pending | running | completed | failed
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tasks_thread_id ON tasks(thread_id);
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);

-- 创建工具调用日志表
CREATE TABLE IF NOT EXISTS tool_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id VARCHAR(255),
    tool_name VARCHAR(100) NOT NULL,
    arguments JSONB,
    result JSONB,
    status VARCHAR(50),                   -- success | error
    latency_ms INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_tool_logs_thread_id ON tool_logs(thread_id);

-- 创建测试数据（可选）
-- INSERT INTO long_term_memory (user_id, memory_type, content) 
-- VALUES ('test_user', 'preference', '喜欢学习 Python 和 LangGraph');

