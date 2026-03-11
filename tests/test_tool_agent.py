"""
Tool Agent 测试
"""
import asyncio
from langchain_core.messages import HumanMessage
from intentrouter.graph.main_graph import create_graph


async def test_tool_agent():
    """测试 Tool Agent"""
    app = create_graph()



    test_cases = [
        # 时间工具
        # {
        #     "input": "现在几点了？",
        #     "expected_intent": "tool_call",
        #     "expected_tool": "get_current_time"
        # },
        # # 计算器
        # {
        #     "input": "帮我计算 123 * 456 + 789",
        #     "expected_intent": "tool_call",
        #     "expected_tool": "calculator"
        # },
        # 搜索工具
        {
            "input": "搜索一下最新热搜内容",
            "expected_intent": "tool_call",
            "expected_tool": "web_search"
        },
        # # 文件读取
        # {
        #     "input": "读取 README.md 文件的内容",
        #     "expected_intent": "tool_call",
        #     "expected_tool": "read_file"
        # },
        # # 天气工具
        # {
        #     "input": "北京今天天气怎么样？",
        #     "expected_intent": "tool_call",
        #     "expected_tool": "get_weather"
        # },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"测试用例 {i}/{len(test_cases)}")
        print(f"输入: {test['input']}")

        result = app.invoke({
            "messages": [HumanMessage(content=test["input"])],
            "thread_id": f"test-{i}"
        }, config={"configurable": {"thread_id": f"test-{i}"}})

        # 验证结果
        intent = result.get("intent")
        tools_used = result.get("tools_used", [])
        final_message = result["messages"][-1].content

        print(f"识别意图: {intent}")
        print(f"使用工具: {tools_used}")
        print(f"最终回复: {final_message[:200]}...")

        # 简单断言
        if intent == test["expected_intent"]:
            print("✅ 意图识别正确")
        else:
            print(f"❌ 意图识别错误（预期: {test['expected_intent']}）")

        if test["expected_tool"] in tools_used:
            print("✅ 工具调用正确")
        else:
            print(f"❌ 工具调用错误（预期: {test['expected_tool']}）")


if __name__ == "__main__":
    asyncio.run(test_tool_agent())