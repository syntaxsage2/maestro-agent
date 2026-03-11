"""
测试 Tool Agent 调用 MCP 工具
"""
import asyncio
from langchain_core.messages import HumanMessage
from intentrouter.graph.main_graph import create_graph


async def test_mcp_with_agent():
    """测试 Agent 使用 MCP 工具"""
    
    # 🆕 加载 MCP 工具
    print("🔄 正在加载 MCP 工具...")
    from intentrouter.tools.builtin import register_mcp_tools
    from intentrouter.tools.registry import tools_registry
    
    await register_mcp_tools()
    
    print(f"✅ 已加载 {len(tools_registry.list_tools())} 个工具")
    print(f"📋 可用工具: {tools_registry.list_tools()}\n")

    app = create_graph()

    test_cases = [
        "列出当前目录的所在位置",
        # "读取 README.md 文件的内容",
        # "在 intentrouter 目录下有哪些文件和文件夹？",
    ]

    for i, query in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"测试 {i}: {query}")
        print("=" * 80)

        result = app.invoke({
            "messages": [HumanMessage(content=query)],
            "thread_id": f"test-mcp-{i}-5"
        }, config={"configurable": {"thread_id": f"test-mcp-{i}-5"}})

        print(f"\n意图: {result.get('intent')}")
        print(f"路由: {result.get('route_decision')}")
        print(f"使用工具: {result.get('tools_used', [])}")
        print(f"\n回复:\n{result['messages'][-1].content[:500]}...")


if __name__ == "__main__":
    asyncio.run(test_mcp_with_agent())