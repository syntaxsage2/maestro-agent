"""
可复用Runnable组件
将Agent节点包装为Runnable, 便于并行组合
"""
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable, RunnableLambda

from intentrouter.graph.nodes.rag_agent import rag_agent_node
from intentrouter.graph.nodes.tool_agent import tool_call_node


class RAGAgentRunnable(Runnable):
    """RAG Agent 的 Runnable 封装"""
    def __init__(self, goal: str = None):
        """
        Args:
            goal: 子任务目标(覆盖原始用户信息)
        """
        self.goal = goal

    def invoke(self, input: dict, config: dict = None, **kwargs) -> dict:
        """同步调用"""
        # 如果制定了goal，会创建新的消息
        if self.goal:
            input = {
                **input,
                "messages": input["messages"][:-1] + [HumanMessage(content=self.goal)],
            }
        return rag_agent_node(input)

    async def ainvoke(self, input: dict, config: dict = None, **kwargs) -> dict:
        """异步调用"""
        if self.goal:
            input = {
                **input,
                "messages": input["messages"][:-1] + [HumanMessage(content=self.goal)]
            }

            # 如果 rag_agent_node 不是异步的，用同步版本
        return rag_agent_node(input)


class ToolAgentRunnable(Runnable):
    """Tool Agent 的Runnable 封装"""

    def __init__(self, goal: str = None):
        """
        Args:
            goal: 子任务目标
        """
        self.goal = goal

    def invoke(self, input: dict, config: dict = None, **kwargs) -> dict:
        """同步调用"""
        if self.goal:
            input = {
                **input,
                "messages": input["messages"][:-1] + [HumanMessage(content=self.goal)]
            }

        return tool_call_node(input)

    async def ainvoke(self, input: dict, config: dict = None, **kwargs) -> dict:
        """异步调用"""
        if self.goal:
            input = {
                **input,
                "messages": input["messages"][:-1] + [HumanMessage(content=self.goal)]
            }

        return tool_call_node(input)


def create_step_runnable(step: dict) -> Runnable:
    """
    根据步骤定义创建对应的 Runnable

    Args:
        step:步骤定义
    Returns:
        Runnable: 可执行的Runnable
    """
    step_type = step["type"]
    goal = step["goal"]

    if step_type == "rag_agent":
        return RAGAgentRunnable(goal)
    elif step_type == "tool_agent":
        return ToolAgentRunnable(goal)
    elif step_type == "synthesis":
        # Synthesis 步骤在 Executor 中单独处理
        return RunnableLambda(lambda x: {"type": "synthesis", "content": "待综合"})
    else:
        raise ValueError(f"未知的步骤类型: {step_type}")

