"""
测试真实的 MCP 连接
"""
import asyncio
from intentrouter.mcp.MCP_manager  import get_mcp_manager


async def test_mcp_connection():
    """测试连接到 MCP Server"""

    print("🚀 测试 MCP 连接\n")

    # 获取 Manager
    manager = await get_mcp_manager()

    # 查看加载的工具
    tools = manager.get_all_tools()

    print(f"\n✅ 加载了 {len(tools)} 个 MCP 工具：")
    for tool in tools:
        print(f"\n🔧 {tool.name}")
        print(f"   描述: {tool.description[:60]}...")
        print(f"   来源: {tool.metadata.get('server', 'unknown')}")

    # 测试调用工具
    if tools:
        print(f"\n🧪 测试调用第一个工具...")

        first_tool = tools[0]
        print(f"工具名称: {first_tool.name}")

        # 根据工具类型调用
        if "list" in first_tool.name or "directory" in first_tool.name:
            # 列出目录
            result = await first_tool.ainvoke({"path": "."})
            print(f"\n结果:\n{result[:500]}")
        elif "read" in first_tool.name:
            # 读取文件
            result = await first_tool.ainvoke({"path": "README.md"})
            print(f"\n结果:\n{result[:500]}")

    # 清理
    await manager.disconnect_all()

    print("\n✅ 测试完成！")


if __name__ == "__main__":
    asyncio.run(test_mcp_connection())