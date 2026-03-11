"""
应用启动初始化
"""
import asyncio
from intentrouter.tools.builtin import register_mcp_tools


async def initialize_mcp_tools():
    """初始化 MCP 工具"""
    print("🚀 正在初始化 MCP 工具...")
    await register_mcp_tools()
    print("✅ MCP 工具初始化完成")


def startup():
    """应用启动入口"""
    try:
        # 运行异步初始化
        asyncio.run(initialize_mcp_tools())
    except Exception as e:
        print(f"⚠️ MCP 初始化失败: {e}")
        print("将使用内置工具运行")