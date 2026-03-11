"""
FastAPI主应用
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from intentrouter.api.routes import chat, history, auth
from intentrouter.api.routes import hitl, state
from intentrouter.api.middleware import (
    RequestLoggingMiddleware,
    ErrorHandlingMiddleware,
    RateLimitMiddleware
)
from intentrouter.config import settings
# 导入 tools 模块以触发工具注册
import intentrouter.tools  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理

    startup: yield 之前的代码
    shutdown: yield 之后的代码
    """
    # ===== Startup =====
    print("🚀 启动 IntentRouter Pro API...")

    # 初始化 Checkpointer
    try:
        from intentrouter.db.checkpointer import get_async_checkpointer
        print("🔄 正在初始化 Checkpointer...")
        await get_async_checkpointer()
        print("✅ Checkpointer 初始化完成")
    except Exception as e:
        print(f"⚠️ Checkpointer 初始化失败: {e}")
        print("将在首次使用时重试")

    # 🆕 初始化 MCP 工具
    try:
        from intentrouter.tools.builtin import register_mcp_tools
        from intentrouter.tools.registry import tools_registry

        print("🔄 正在加载 MCP 工具...")
        await register_mcp_tools()

        tool_count = len(tools_registry.list_tools())
        mcp_loaded = tools_registry.is_mcp_loaded()

        print(f"✅ MCP 工具已加载")
        print(f"📊 可用工具数: {tool_count}")
        print(f"🔧 MCP 状态: {'已启用' if mcp_loaded else '未启用'}")

    except Exception as e:
        print(f"⚠️ MCP 工具加载失败: {e}")
        print("将继续使用内置工具运行")

    print("✅ API 启动完成\n")

    # ===== 应用运行中 =====
    yield

    # ===== Shutdown =====
    print("\n🛑 正在关闭 IntentRouter Pro API...")

    # 清理 Checkpointer
    try:
        from intentrouter.db.checkpointer import close_checkpointer
        await close_checkpointer()
        print("✅ Checkpointer 已关闭")
    except Exception as e:
        print(f"⚠️ Checkpointer 清理失败: {e}")

    # 清理 MCP 连接
    try:
        from intentrouter.mcp.MCP_manager import get_mcp_manager

        manager = await get_mcp_manager()
        await manager.disconnect_all()
        print("✅ MCP 连接已清理")
    except Exception as e:
        print(f"⚠️ MCP 清理失败: {e}")

    print("✅ API 已关闭")


# 创建 FastAPI 应用（使用 lifespan）
app = FastAPI(
    title="IntentRouter Pro API",
    description="意图驱动的 Agent 系统 - 支持意图识别、RAG、工具调用、多模态、HITL",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ===== 配置 CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React 默认端口
        "http://localhost:8501",  # Streamlit 默认端口
        "http://localhost:5173",  # Vite 默认端口
        "*"  # ⚠️ 生产环境应指定具体域名
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Thread-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"]
)

# ===== 添加中间件（按顺序）=====
# 1. 错误处理（最外层）
app.add_middleware(ErrorHandlingMiddleware)

# 2. 请求日志
app.add_middleware(RequestLoggingMiddleware)

# 3. 速率限制（可选，开发时可以注释掉）
app.add_middleware(RateLimitMiddleware, max_requests=100, window=60)

# ===== 注册路由 =====
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(hitl.router, prefix="/api", tags=["HITL"])
app.include_router(state.router, prefix="/api", tags=["State"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "IntentRouter Pro API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """健康检查"""
    from intentrouter.tools.registry import tools_registry

    return {
        "status": "healthy",
        "tools_count": len(tools_registry.list_tools()),
        "mcp_loaded": tools_registry.is_mcp_loaded(),
        "tools": tools_registry.list_tools()
    }


@app.get("/tools")
async def list_tools():
    """列出所有可用工具"""
    from intentrouter.tools.registry import tools_registry

    tools = tools_registry.get_all_tools()

    tool_info = []
    for tool in tools:
        info = {
            "name": tool.name,
            "description": tool.description[:100] + "..." if len(tool.description) > 100 else tool.description,
            "source": tool.metadata.get("source", "builtin") if hasattr(tool, "metadata") else "builtin"
        }
        tool_info.append(info)

    return {
        "total": len(tool_info),
        "mcp_loaded": tools_registry.is_mcp_loaded(),
        "tools": tool_info
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "intentrouter.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True  # 开发模式自动重载
    )