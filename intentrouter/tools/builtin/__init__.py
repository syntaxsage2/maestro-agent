"""
内置工具自动注册
"""
from intentrouter.tools.builtin.calculator_tool import calculator
from intentrouter.tools.builtin.file_tool import read_file, delete_file
from intentrouter.tools.builtin.search_tool import web_search
from intentrouter.tools.builtin.time_tool import get_current_time
from intentrouter.tools.builtin.weather_tool import get_weather
from intentrouter.tools.registry import tools_registry


def register_builtin_tools():
    """注册所有内置工具"""
    tools_registry.register(get_current_time)
    tools_registry.register(calculator)
    tools_registry.register(web_search)
    tools_registry.register(read_file)
    tools_registry.register(delete_file)  # 🆕 注册删除文件工具
    tools_registry.register(get_weather)

    print(f"✅ 已注册 {len(tools_registry.list_tools())} 个内置工具")


async def register_mcp_tools():
    """注册 MCP 工具（异步）"""
    try:
        from intentrouter.mcp.MCP_manager import get_mcp_manager

        print("🔄 开始加载 MCP 工具...")
        manager = await get_mcp_manager()

        # 注册所有 MCP 工具
        mcp_tools = manager.get_all_tools()
        for tool in mcp_tools:
            tools_registry.register(tool)

        print(f"✅ 已注册 {len(mcp_tools)} 个 MCP 工具")
        
        # 🆕 标记 MCP 已加载
        tools_registry.mark_mcp_loaded()

    except Exception as e:
        print(f"⚠️ MCP 工具加载失败: {e}")
        import traceback
        traceback.print_exc()
        print("继续使用内置工具...")


# 🔴 只自动注册内置工具
register_builtin_tools()

# 🔴 MCP 工具不在这里加载！
# 会在 Tool Agent 首次使用时加载