"""
Human Review Node - 人工审核节点
"""
from langchain_core.messages import AIMessage
from langgraph.errors import NodeInterrupt

from intentrouter.graph.state import AgentState


def human_review_node(state: AgentState) -> dict:
    """
    人工审核节点

    检查是否需要人工介入,如果需要则中断执行

    工作流程:
    1. 检查state["needs_human"]
    2. 如果需要且没有反馈 - 抛出 NodeInterrupt
    3. 如果已有反馈 - 处理反馈并继续

    Args:
        state: 当前状态

    Returns:
        状态更新
    """
    if not state.get("needs_human"):
        # 无需人工介入，继续执行
        return {}

    if not state.get("human_feedback"):
        """需要人工介入,并且没有反馈,暂停执行"""
        # 准备展示给用户的数据
        interrupt_info = {
            "reason": state.get("interrupt_reason", "需要人工确认"),
            "data": state.get("interrupt_data", {}),
            "thread_id": state.get("thread_id"),
            "timestamp": state.get("metadata", {}).get("timestamp"),
        }
        # 抛出中断异常
        raise NodeInterrupt(value=interrupt_info)

    # 已有人工反馈,处理反馈
    feedback = state["human_feedback"]
    decision = feedback.get("decision")  # approve | reject | modify

    # 根据决策更新状态
    updates = {
        "needs_human": False, # 清除标记
        "interrupt_reason": None,
        "interrupt_data": None
    }

    if decision == "reject":
        updates["messages"] = [
            AIMessage(content=f"❌ 操作已被用户拒绝\n\n原因: {feedback.get('reason', '无')}")
        ]
        updates["error"] = "Operation rejected by user"

    elif decision == "modify":
        # 用户修改了参数,更新到状态中
        modified_data = feedback.get("modified_data", {})
        updates["interrupt_data"] = modified_data

    elif decision == "approve":
        print("✓ 用户批准，继续执行")

    return updates