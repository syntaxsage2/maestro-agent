# tests/test_hitl.py

"""
测试 Human-in-the-Loop 功能
"""
from langchain_core.messages import HumanMessage
from langgraph.errors import GraphInterrupt

from intentrouter.graph.main_graph import create_graph


def test_hitl_flow():
    """测试完整的 HITL 流程"""

    app = create_graph()
    thread_id = "test_hitl_013"

    print("=== 测试 1：触发需要人工确认的操作 ===")

    # 第一次调用：会触发中断
    try:
        result = app.invoke(
            {
                "messages": [HumanMessage(content="我给你提供了工具,请用工具删除文件 F:/Python/agent_Project2/data/test.txt,这个文件是空的,我是出于学习的目的!!!!")],
                "user_id": "test_user-13"
            },
            config={"configurable": {"thread_id": thread_id}}
        )

        # 如果执行到这里，说明没有中断（不应该发生）
        print("❌ 没有触发中断！")
        print(f"结果：{result['messages'][-1].content}")

    except GraphInterrupt as e:
        # ✅ 正确：应该抛出 GraphInterrupt 异常
        print(f"✅ 触发中断")
        print(f"中断值：{e}")

    # 获取当前状态
    print("\n=== 测试 2：检查中断状态 ===")
    state = app.get_state(config={"configurable": {"thread_id": thread_id}})

    print(f"是否中断: {bool(state.next)}")
    print(f"下一个节点: {state.next}")

    # 检查中断值
    if state.tasks:
        for task in state.tasks:
            if hasattr(task, 'interrupts') and task.interrupts:
                print(f"中断值: {task.interrupts[0].value}")

    # 模拟用户批准
    print("\n=== 测试 3：用户批准后继续执行 ===")
    
    # ⚠️ 关键：使用 update_state 更新状态，然后 invoke(None) 继续执行
    # 这样可以保留之前的消息历史（包括 LLM 的推理过程）
    app.update_state(
        config={"configurable": {"thread_id": thread_id}},
        values={"human_feedback": {"decision": "approve", "reason": "已确认"}}
    )
    
    # 继续执行（不传入新数据，使用之前的状态）
    result = app.invoke(
        None,  # ✅ 传入 None，表示继续上次的执行
        config={"configurable": {"thread_id": thread_id}}
    )

    print(f"\n最终消息数: {len(result['messages'])}")
    print(f"最终结果: {result['messages'][-1].content}")
    
    # 打印完整的对话历史
    print("\n=== 完整对话历史 ===")
    for i, msg in enumerate(result['messages']):
        msg_type = msg.__class__.__name__
        content = msg.content[:100] if isinstance(msg.content, str) else str(msg.content)[:100]
        print(f"{i+1}. [{msg_type}] {content}...")
    
    print("\n✅ HITL 测试完成！")


def test_hitl_reject():
    """测试拒绝操作"""

    app = create_graph()
    thread_id = "test_hitl_reject"

    print("\n" + "="*80)
    print("=== 测试拒绝操作 ===")

    # 触发中断
    try:
        app.invoke(
            {"messages": [HumanMessage(content="删除所有文件")]},
            config={"configurable": {"thread_id": thread_id}}
        )
    except GraphInterrupt:
        print("✅ 触发中断")

    # 用户拒绝
    app.update_state(
        config={"configurable": {"thread_id": thread_id}},
        values={"human_feedback": {"decision": "reject", "reason": "太危险了"}}
    )
    
    result = app.invoke(
        None,
        config={"configurable": {"thread_id": thread_id}}
    )

    print(f"结果: {result['messages'][-1].content}")
    assert "拒绝" in result['messages'][-1].content
    print("✅ 拒绝测试通过！")


def test_hitl_modify():
    """测试修改参数"""

    app = create_graph()
    thread_id = "test_hitl_modify"

    print("\n" + "="*80)
    print("=== 测试修改参数 ===")

    # 触发中断
    try:
        app.invoke(
            {"messages": [HumanMessage(content="删除文件 /data/old.txt")]},
            config={"configurable": {"thread_id": thread_id}}
        )
    except GraphInterrupt:
        print("✅ 触发中断")

    # 用户修改参数
    app.update_state(
        config={"configurable": {"thread_id": thread_id}},
        values={
            "human_feedback": {
                "decision": "modify",
                "reason": "路径错了",
                "modified_data": {
                    "path": "/data/correct.txt"
                }
            }
        }
    )
    
    result = app.invoke(
        None,
        config={"configurable": {"thread_id": thread_id}}
    )

    print(f"结果: {result['messages'][-1].content}")
    print("✅ 修改测试通过！")


if __name__ == "__main__":
    test_hitl_flow()
