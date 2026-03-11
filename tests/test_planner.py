"""
Planner Agent 测试
"""
import asyncio
from langchain_core.messages import HumanMessage
from intentrouter.graph.main_graph import create_graph


async def test_planner():
    """测试 Planner Agent"""
    app = create_graph()

    test_cases = [
        # 简单的复杂任务
        {
            "input": "帮我调研一下 LangGraph 的核心功能，你先搜索相关信息,并结合知识库, 二者总结，然后生成一份技术总结",
            "expected_steps": 3  # RAG + Search + Synthesis
        },
        # # 多数据源综合
        # {
        #     "input": "查询今天的天气，查看我的日程安排，然后告诉我今天应该做什么准备",
        #     "expected_steps": 3  # Weather + Calendar + Synthesis
        # },
        # # 知识+计算
        # {
        #     "input": "帮我计算 123 * 456，然后从知识库中找到相关的数学概念解释",
        #     "expected_steps": 3  # Calculator + RAG + Synthesis
        # },
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 80}")
        print(f"测试用例 {i}/{len(test_cases)}")
        print(f"输入: {test['input']}")
        print("=" * 80)

        result = app.invoke({
            "messages": [HumanMessage(content=test["input"])],
            "thread_id": f"test-planner-{i}"
        }, config={"configurable": {"thread_id": f"test-planner-{i}"}})

        # 查看结果
        intent = result.get("intent")
        plan = result.get("plan")
        subtask_results = result.get("subtask_results", {})
        final_message = result["messages"][-1].content

        print(f"\n识别意图: {intent}")

        if plan:
            print(f"\n📋 执行计划:")
            print(f"  任务: {plan.get('task_summary', 'N/A')}")
            print(f"  步骤数: {len(plan.get('steps', []))}")
            for step in plan.get("steps", []):
                print(f"    - {step['id']}: {step['type']} | {step['goal']}")

        if subtask_results:
            print(f"\n✅ 执行结果:")
            for step_id, result in subtask_results.items():
                status = "✅" if result.get("success") else "❌"
                print(f"    {status} {step_id}: {result.get('type', 'unknown')}")

        print(f"\n📝 最终回复:")
        print(f"{final_message[:300]}...")

        # 验证
        if intent == "complex_task":
            print("\n✅ 意图识别正确")
        else:
            print(f"\n⚠️  意图识别为: {intent}（可能不需要规划）")

        if plan and len(plan.get("steps", [])) >= test["expected_steps"]:
            print("✅ 计划生成正确")
        else:
            print(f"⚠️  步骤数不符（预期 >= {test['expected_steps']}）")


if __name__ == "__main__":
    asyncio.run(test_planner())