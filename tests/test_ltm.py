"""
测试长期记忆系统
"""
import time
from langchain_core.messages import HumanMessage

from intentrouter.graph.main_graph import create_graph


def test_long_term_memory():
    """测试长期记忆的完整流程"""

    app = create_graph()
    user_id = "test_user_ltm-3"

    print("=== 测试1：建立用户画像 ===")
    test_cases = [
        "你好，我叫张三，是一名Python开发工程师",
        "我正在学习LangGraph和Agent开发",
        "我喜欢写简洁优雅的代码，习惯使用类型提示",
    ]

    for i, user_input in enumerate(test_cases, 1):
        print(f"\n--- 对话 {i} ---")
        print(f"用户: {user_input}")

        # 使用同步调用（PostgresSaver 不支持异步）
        result = app.invoke(
            {
                "messages": [HumanMessage(content=user_input)],
                "user_id": user_id
            },
            config={"configurable": {"thread_id": f"ltm_test_{i}-3"}}
        )

        print(f"助手: {result['messages'][-1].content}")

    print("\n" + "=" * 80)
    print("=== 测试2：检查记忆是否被提取 ===")

    # 等待一下让记忆写入完成
    time.sleep(1)

    from intentrouter.db.ltm_manager import get_ltm_manager
    ltm_manager = get_ltm_manager()

    profile = ltm_manager.get_user_profile(user_id)
    print(f"\n用户画像:")
    print(f"  事实: {profile['facts']}")
    print(f"  偏好: {profile['preferences']}")
    print(f"  技能: {profile['skills']}")

    print("\n" + "=" * 80)
    print("=== 测试3：新对话中应用记忆 ===")

    result = app.invoke(
        {
            "messages": [HumanMessage(content="你知道我是谁吗？我的技能是什么？")],
            "user_id": user_id
        },
        config={"configurable": {"thread_id": "ltm_test_recall-1"}}
    )

    print(f"\n用户: 你知道我是谁吗？我的技能是什么？")
    print(f"助手: {result['messages'][-1].content}")

    print("\n✅ 测试完成！")


if __name__ == "__main__":
    test_long_term_memory()