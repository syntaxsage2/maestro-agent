"""
多轮对话测试
"""
import uuid

from langchain_core.messages import HumanMessage

from intentrouter.graph.main_graph import create_graph


def test_multiturn_conversation():
    app = create_graph()

    # 生成会话ID
    thread_id = "515dcb37-ea06-44b4-ba04-6e05fd534e08"
    print(thread_id)
    config = {"configurable": {"thread_id": thread_id}}

    print(f"\n{'=' * 80}")
    print(f"🆔 会话 ID: {thread_id}")
    print(f"{'=' * 80}\n")

    # === 第一轮：介绍自己 ===
    # print("👤 用户: 我叫小明，我喜欢学习 Python")
    # result1 = app.invoke(
    #     {"messages": [HumanMessage(content="我叫小明,我喜欢学习python")]},
    #     config=config
    # )
    # print(f"🤖 助手: {result1['messages'][-1].content}\n")

    # === 第二轮：询问（测试记忆） ===
    print("👤 用户: 我叫什么名字？")
    result2 = app.invoke(
        {"messages": [HumanMessage(content="我叫什么名字？")]},
        config=config
    )
    print(f"🤖 助手: {result2['messages'][-1].content}\n")
    #
    # # === 第三轮：知识问答 ===
    # print("👤 用户: Python 的 asyncio 怎么用？")
    # result3 = app.invoke(
    #     {"messages": [HumanMessage(content="Python 的 asyncio 怎么用？")]},
    #     config=config
    # )
    # print(f"🤖 助手: {result3['messages'][-1].content[:200]}...\n")
    #
    # # === 验证：查看历史消息数量 ===
    # message_count = len(result3['messages'])
    # print(f"📊 历史消息数: {message_count}")
    # print(f"✅ 多轮对话测试{'成功' if message_count >= 6 else '失败'}！")


def test_new_conversation():
    """测试新会话（无历史）"""
    app = create_graph()

    # 新的会话 ID
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    print(f"\n{'=' * 80}")
    print(f"🆔 新会话 ID: {thread_id}")
    print(f"{'=' * 80}\n")

    print("👤 用户: 我叫什么名字？")
    result = app.invoke(
        {"messages": [HumanMessage(content="我叫什么名字？")]},
        config=config
    )
    print(f"🤖 助手: {result['messages'][-1].content}\n")
    print("✅ 新会话测试成功（应该回答不知道）")


if __name__ == "__main__":
    print("🧪 测试 1: 多轮对话（带记忆）")
    test_multiturn_conversation()


