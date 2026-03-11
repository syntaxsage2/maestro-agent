# 运维配置

## ? 快速启动 PostgreSQL

### 方法 1：使用 Docker Compose（推荐）

```bash
# 1. 进入 ops 目录
cd ops

# 2. 启动 PostgreSQL
docker-compose up -d

# 3. 检查状态
docker-compose ps

# 4. 查看日志
docker-compose logs -f postgres

# 5. 停止
docker-compose down

# 6. 停止并删除数据（慎用！）
docker-compose down -v
```

### 方法 2：直接使用 Docker

```bash
docker run -d \
  --name intentrouter_postgres \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password123 \
  -e POSTGRES_DB=intentrouter \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  postgres:16-alpine
```

---

## ? 连接测试

### 使用 psql（命令行工具）

```bash
# 如果安装了 PostgreSQL 客户端
psql -h localhost -U admin -d intentrouter -p 5432

# 使用 Docker 进入容器
docker exec -it intentrouter_postgres psql -U admin -d intentrouter
```

### 使用 Python

```python
import psycopg

conn = psycopg.connect(
    "postgresql://admin:password123@localhost:5432/intentrouter"
)
print("? 连接成功")

# 查看表
with conn.cursor() as cur:
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    print("数据库表:", tables)

conn.close()
```

---

## ? 数据库管理

### 查看 Checkpoints

```sql
-- 查看所有会话
SELECT DISTINCT thread_id, COUNT(*) as checkpoint_count
FROM checkpoints
GROUP BY thread_id
ORDER BY MAX(checkpoint_id) DESC;

-- 查看特定会话的历史
SELECT checkpoint_id, checkpoint_ns, type, metadata
FROM checkpoints
WHERE thread_id = 'your_thread_id_here'
ORDER BY checkpoint_id;

-- 清理旧会话（保留最近 7 天）
DELETE FROM checkpoints
WHERE checkpoint_id < (
    SELECT MAX(checkpoint_id) - 7*24*60*60*1000
    FROM checkpoints
);
```

### 查看任务记录

```sql
-- 查看最近的任务
SELECT * FROM tasks
ORDER BY created_at DESC
LIMIT 10;

-- 统计各意图的数量
SELECT intent, COUNT(*) as count
FROM tasks
GROUP BY intent
ORDER BY count DESC;
```

---

## ?? 故障排查

### 端口被占用

```bash
# Windows
netstat -ano | findstr :5432

# Linux/Mac
lsof -i :5432
```

解决：
1. 停止占用的进程
2. 或修改 `docker-compose.yml` 中的端口映射：`"5433:5432"`

### 连接被拒绝

检查：
1. Docker 容器是否运行：`docker-compose ps`
2. 端口是否正确
3. 防火墙设置

### 数据持久化

数据存储在 Docker Volume `postgres_data` 中：

```bash
# 查看 Volume
docker volume ls

# 查看详情
docker volume inspect intentrouter_postgres_data

# 备份数据
docker exec intentrouter_postgres pg_dump -U admin intentrouter > backup.sql

# 恢复数据
docker exec -i intentrouter_postgres psql -U admin intentrouter < backup.sql
```

---

## ? 下一步

PostgreSQL 启动成功后，继续 Step 4 的其他任务。

