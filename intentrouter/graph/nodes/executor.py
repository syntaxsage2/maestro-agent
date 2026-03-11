"""
Executor 节点 - 执行计划调度器
"""
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage

from intentrouter.config import settings
from intentrouter.graph.nodes.rag_agent import rag_agent_node
from intentrouter.graph.nodes.tool_agent import tool_call_node
from intentrouter.graph.prompts import SYNTHESIS_PROMPT
from intentrouter.graph.state import AgentState


def executor_node(state: AgentState) -> dict:
    """
    Executor 节点 - 根据计划调度子任务

    流程:
    1. 解析计划依赖关系
    2. 按优先级分组
    3. 并行执行同优先级任务
    4. 收集结果
    5. 执行综合步骤

     Args:
        state: Agent 状态

    Returns:
        dict: 状态更新
    """

    plan = state.get("plan")

    if not plan or not plan.get("steps"):
        return {
            "error": "没有有效执行计划",
            "messages": [AIMessage(content="执行计划为空")]
        }

    steps = plan["steps"]
    # 1. 按优先级处理
    priority_groups = _group_by_priority(steps)

    # 2.存储所有步骤结果
    all_results = {}
    execution_messages = []

    # 3.按优先级依次执行（串行执行，原来的并行改为串行）
    for priority in sorted(priority_groups.keys()):
        group_steps = priority_groups[priority]

        print(f"\n🔄 执行优先级 {priority} 的任务（共 {len(group_steps)} 个）...")

        # 串行执行该组所有步骤
        for step in group_steps:
            try:
                result = _execute_step(step, state, all_results)
                all_results[step["id"]] = result
                print(f"✅ 步骤 {step['id']} 完成")
            except Exception as e:
                all_results[step["id"]] = {
                    "success": False,
                    "error": str(e),
                }
                print(f"❌ 步骤 {step['id']} 失败: {e}")

    # 4.检查是否有综合步骤
    synthesis_steps = [s for s in steps if s["type"] == "synthesis"]

    if synthesis_steps:
        # 执行综合生成
        final_content = _synthesize_results(
            all_results,
            state["messages"][-1].content,  # 原始用户请求
            state
        )

        return {
            "subtask_results": all_results,
            "messages": [AIMessage(content=final_content)]
        }
    else:
        # 没有综合步骤，直接返回所有结果
        summary = _format_results(all_results)

        return {
            "subtask_results": all_results,
            "messages": [AIMessage(content=summary)]
        }


def _group_by_priority(steps: list[dict]) -> dict[int, list[dict]]:
    """
    按优先级分组步骤

    Args:
        steps:步骤列表

    Returns:
        优先级分组
    """
    groups = {}
    for step in steps:
        priority = step.get("priority", 999)
        if priority not in groups:
            groups[priority] = []
        groups[priority].append(step)
    return groups

def _execute_step(step: dict, state: AgentState, all_results: dict) -> dict:
    """
    执行单个步骤

    Args:
        step: 步骤定义
        state: 当前状态
        previous_results: 之前步骤的结果

    Returns:
        dict: 执行结果
    """
    step_type = step["type"]
    step_goal = step["goal"]

    # 构建步骤的临时是state
    step_state = {
        **state,
        "messages": state["messages"] + [HumanMessage(content=step_goal)]
    }

    try:
        if step_type == "rag_agent":
            # 调用 RAG Agent
            result = rag_agent_node(step_state)
            return {
                "success": True,
                "type": "rag_agent",
                "content": result["messages"][-1].content if result.get("messages") else "",
                "retrieved_docs": result.get("retrieved_docs", [])
            }
        elif step_type == "tool_agent":
            # 调用 Tool Agent
            result = tool_call_node(step_state)
            return {
                "success": True,
                "type": "tool_agent",
                "content": result["messages"][-1].content if result.get("messages") else "",
                "tools_used": result.get("tools_used", []),
                "tool_results": result.get("tool_results", {})
            }
        elif step_type == "synthesis":
            # 综合步骤在后面统一处理
            return {
                "success": True,
                "type": "synthesis",
                "content": "等待综合..."
            }

        else:
            raise ValueError(f"未知的步骤类型: {step_type}")

    except Exception as e:
        return {
            "success": False,
            "type": step_type,
            "error": str(e)
        }


def _synthesize_results(
        results: dict[str, Any],
        original_query: str,
        state: AgentState
) -> str:
    """
       综合所有步骤的结果，生成最终答案

       Args:
           results: 所有步骤的结果
           original_query: 用户原始请求
           state: 当前状态

       Returns:
           str: 综合后的最终答案
       """
    # 格式化结果
    results_text = _format_results(results)

    # 构建 Prompt
    prompt = SYNTHESIS_PROMPT.format(
        results=results_text,
        original_query=original_query
    )

    # 调用 LLM 生成
    llm = init_chat_model(
        model="gpt-4o-mini",
        model_provider="openai",
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
        temperature=0.3,
    )
    response = llm.invoke([HumanMessage(content=prompt)])

    return response.content



def _format_results(result: dict[str, Any]) -> str:
    """
    格式化结果为文本

    Args:
        results: 步骤结果字典

    Returns:
        str: 格式化的文本
    """
    formatted = []

    for step_id, result in result.items():
        formatted.append(f"##{step_id}")
        formatted.append(f"- 类型:{result.get('type', 'unknown')}")
        formatted.append(f"- 状态:{'成功' if result.get('success') else '失败'}")

    if result.get("success"):
        formatted.append(f"- 内容: {result.get('content', 'N/A')[:200]}...")
    else:
        formatted.append(f"- 错误: {result.get('error', 'unknown')}")

    formatted.append("")

    return "\n".join(formatted)