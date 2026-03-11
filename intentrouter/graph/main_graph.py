from langgraph.graph import StateGraph, START, END

from intentrouter.config import settings
from intentrouter.db.checkpointer import get_async_checkpointer
from intentrouter.graph.nodes import memory_extractor
from intentrouter.graph.nodes.executor import executor_node
from intentrouter.graph.nodes.executor_v2 import executor_v2_node
from intentrouter.graph.nodes.human_review import human_review_node
from intentrouter.graph.nodes.memory_extractor import memory_extractor_node
from intentrouter.graph.nodes.planner import planner_node
from intentrouter.graph.nodes.rag_agent import rag_agent_node
from intentrouter.graph.nodes.entry import entry_node
from intentrouter.graph.nodes.output import output_node
from intentrouter.graph.nodes.router import intent_router_node
from intentrouter.graph.nodes.tool_agent import tool_call_node, tool_execute_node
from intentrouter.graph.nodes.vision_agent import vision_agent_node
from intentrouter.graph.state import AgentState
from langchain_core.messages import HumanMessage

from intentrouter.graph.subgraphs.writer_graph import create_writer_subgraph


def route_by_intent(state: AgentState) -> str:
    """
    路由函数:根据state中的route_decision决定下一个节点

    Returns:
        str:节点名称
    """
    decision = state.get("route_decision", "output")
    return decision


def route_after_planner(state: AgentState) -> str:
    """
    planner 之后路由
    如果计划生成成功 → executor
    如果失败 → output
    """
    plan = state.get("plan")
    if plan and plan.get("steps"):
        return "executor"
    else:
        return "output"


def route_after_tool_call(state: AgentState) -> str:
    """
    tool_call 之后路由
    - 如果有 tool_calls → tool_execute（执行工具）
    - 如果没有 tool_calls → output（结束）
    """
    messages = state.get("messages", [])
    if not messages:
        return "output"
    
    last_message = messages[-1]
    
    # 检查是否有工具调用
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tool_execute"
    else:
        return "output"


def route_after_tool_execute(state: AgentState) -> str:
    """
    tool_execute 之后路由
    - 如果迭代次数未达上限 → tool_call（继续循环）
    - 如果达到上限 → output（结束）
    """
    iteration = state.get("tool_iteration", 0)
    
    # 检查是否需要继续
    if iteration < 10:
        return "tool_call"
    else:
        return "output"


async def create_graph():
    # 构建图
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("entry", entry_node)
    graph.add_node("router", intent_router_node)
    graph.add_node("output", output_node)
    graph.add_node("rag_agent", rag_agent_node)
    # Tool Agent 拆分为两个节点
    graph.add_node("tool_call", tool_call_node)
    graph.add_node("tool_execute", tool_execute_node)
    graph.add_node("planner", planner_node)
    graph.add_node("executor", executor_v2_node)
    graph.add_node("vision_agent", vision_agent_node)

    # 添加子图
    writer_subgraph = create_writer_subgraph()
    graph.add_node("writer_agent", writer_subgraph)

    # 记忆提取节点
    graph.add_node("memory_extractor", memory_extractor_node)

    # 添加边
    graph.add_edge(START, "entry")
    graph.add_edge("entry", "router")

    # 条件路由
    graph.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "output": "output",
            "rag_agent": "rag_agent",
            "planner": "planner",
            "tool_agent": "tool_call",  # 改为 tool_call 节点
            "writer_agent": "writer_agent",
            "vision_agent": "vision_agent",
        }
    )

    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {
            "executor": "executor",
            "output": "output",
        }
    )

    # Tool Agent 循环路由
    graph.add_conditional_edges(
        "tool_call",
        route_after_tool_call,
        {
            "tool_execute": "tool_execute",
            "output": "output",
        }
    )

    graph.add_conditional_edges(
        "tool_execute",
        route_after_tool_execute,
        {
            "tool_call": "tool_call",
            "output": "output",
        }
    )

    graph.add_edge("rag_agent", "output")
    graph.add_edge("writer_agent", "output")
    graph.add_edge("executor", "output")
    graph.add_edge("vision_agent", "output")
    graph.add_edge("output", "memory_extractor")
    graph.add_edge("memory_extractor", END)

    checkpointer = await get_async_checkpointer()
    return graph.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    import asyncio
    #
    # async def main():
    #     app = await create_graph()
    #
    #     test_cases = [
    #         # ("你好", "general_chat"),
    #     ("Python 的 asyncio 怎么用？", "simple_qa"),
    #     ("什么是 LangGraph？", "simple_qa"),
    #     # ("Chroma 和 FAISS 有什么区别？", "simple_qa"),
    #     ]
    #
    # for user_input, expected_intent in test_cases:
    #     print(f"\n{'=' * 80}")
    #     print(f"输入:{user_input}")
    #
    #     async for result in app.astream_events({
    #         "messages": [HumanMessage(content=user_input)]
    #     }, version="v1"):
    #         if result["event"] == "on_chain_end" and result["name"] == "LangGraph":
    #             final_state = result["data"]["output"]
    #             print(final_state)
    #             actual_intent = final_state.get("intent")
    #             route = final_state.get("route_decision")
    #             retrieved_count = len(final_state.get("retrieved_docs", []))
    #
    #             print(f"预期意图: {expected_intent}")
    #             print(f"实际意图: {actual_intent}")
    #             print(f"路由目标: {route}")
    #             print(f"检索文档数: {retrieved_count}")
    #             print(f"\n最终回复: \n{final_state['messages'][-1].content}...")
    #
    #             # 简单断言
    #             if actual_intent == expected_intent:
    #                 print("✅ 通过")
    #             else:
    #                 print("❌ 失败")
    #
    # asyncio.run(main())
