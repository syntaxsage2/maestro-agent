"""
Writer subgraph
"""
from langgraph.graph import StateGraph, START, END

from intentrouter.graph.nodes.writer import outline_node, draft_node, refine_node
from intentrouter.graph.state import AgentState


def create_writer_subgraph():
    """
    创建 Writer 子图

    流程: START → Outline → Draft → Refine → END

    Returns:
       StateGraph: Writer 子图
    """
    subgraph = StateGraph(AgentState)

    # 添加节点
    subgraph.add_node("outline", outline_node)
    subgraph.add_node("draft", draft_node)
    subgraph.add_node("refine", refine_node)

    # 添加边
    subgraph.add_edge(START, "outline")
    subgraph.add_edge("outline", "draft")
    subgraph.add_edge("draft", "refine")
    subgraph.add_edge("refine", END)

    return subgraph.compile()
