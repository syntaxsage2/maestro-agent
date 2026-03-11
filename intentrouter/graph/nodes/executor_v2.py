import time
from typing import Any

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnableParallel

from intentrouter.config import settings
from intentrouter.graph.prompts import SYNTHESIS_PROMPT
from intentrouter.graph.runnables import create_step_runnable
from intentrouter.graph.state import AgentState

def executor_v2_node(state: AgentState) -> dict:
    """
    Executor v2 - 使用RunnableParallel 优化并行执行

    优势
    1. 使用LangChain原生并行能力
    2. 自动处理超时和错误
    3. 支持流式输出
    4. 更好性能监控

    Args:
        state: Agent 状态

    Returns:
        dict: 状态更新
    """
    plan = state["plan"]

    if not plan or not plan.get("steps"):
        return {
            "error": "没有有效的执行计划",
            "messages": [AIMessage(content="❌ 执行计划为空")]
        }

    steps = plan["steps"]

    # 1. 按优先级分组
    priority_groups = _group_by_priority(steps)

    # 2. 存储所有步骤结果
    all_results = {}
    start_time = time.time()

    # 3.按优先级并行执行
    for priority in sorted(priority_groups.keys()):
        group_steps = priority_groups[priority]

        print(f"\n🔄 执行优先级 {priority} 的任务（共 {len(group_steps)} 个，使用 RunnableParallel）...")

        # 过滤掉 synthesis 步骤（在最后单独处理)
        executable_steps = [s for s in group_steps if s["type"] != "synthesis"]

        if not executable_steps:
            continue

        # 4. 使用RunnableParallel 并行执行
        if len(executable_steps) == 1:
            # 单个步骤，直接执行
            step = executable_steps[0]
            runnable = create_step_runnable(step)

            try:
                step_start = time.time()
                result = runnable.invoke(state)
                step_time = time.time() - step_start

                all_results[step["id"]] = {
                    "success": True,
                    "type": step["type"],
                    "content": result["messages"][-1].content if result.get("messages") else "",
                    "execution_time": step_time,
                    **_extract_agent_results(step["type"], result)
                }
                print(f"✅ {step['id']} 完成 ({step_time:.2f}s)")
            except Exception as e:
                all_results[step["id"]] = {
                    "success": False,
                    "type": step["type"],
                    "error": str(e)
                }
                print(f"❌ {step['id']} 失败: {e}")

        else:
            # 多个步骤，使用RunnableParallel
            parallel_task = {}
            for step in executable_steps:
                parallel_task[step["id"]] = create_step_runnable(step)

            # 创建并行Runnable
            parallel_runnable = RunnableParallel(parallel_task)

            try:
                parallel_start = time.time()
                # 并行执行所有任务
                parallel_results = parallel_runnable.invoke(state)
                parallel_time = time.time() - parallel_start
                print(f"✅ 并行执行完成 ({parallel_time:.2f}s)")

                # 收集结果
                for step in executable_steps:
                    step_id = step["id"]
                    result = parallel_results[step_id]

                    if isinstance(result, dict) and "error" not in result:
                        all_results[step_id] = {
                            "success": True,
                            "type": step["type"],
                            "content": result["messages"][-1].content if result.get("messages") else "",
                            "execution_time": parallel_time / len(executable_steps),  # 平均时间
                            **_extract_agent_results(step["type"], result)
                        }
                    else:
                        all_results[step_id] = {
                            "success": False,
                            "type": step["type"],
                            "error": str(result.get("error", "Unknown error"))
                        }
            except Exception as e:
                # 并行执行失败，标记所有步骤失败
                for step in executable_steps:
                    all_results[step["id"]] = {
                        "success": False,
                        "type": step["type"],
                        "error": f"并行执行失败: {str(e)}"
                    }
                print(f"❌ 并行执行失败: {e}")

    # 5. 执行综合步骤
    synthesis_steps = [s for s in steps if s["type"] == "synthesis"]

    total_time = time.time() - start_time

    if synthesis_steps:
        final_content = _synthesize_results(
            all_results,
            state["messages"][-1].content,
            state
        )

        return {
            "subtask_results": all_results,
            "messages": [HumanMessage(content=final_content )],
            "metadata": {
                **state.get("metadata", {}),
                "execution_time": total_time,
                "parallel_execution": True
            }
        }

    else:
        # 直接返回结果摘要
        summary = _format_results(all_results, total_time)

        return {
            "subtask_results": all_results,
            "messages": [AIMessage(content=summary)],
            "metadata": {
                **state.get("metadata", {}),
                "execution_time": total_time,
                "parallel_execution": True
            }
        }


def _group_by_priority(steps: list[dict]) -> dict[int, list[dict]]:
    """按优先级分组"""
    groups = {}
    for step in steps:
        priority = step.get("priority", 999)
        if priority not in groups:
            groups[priority] = []
        groups[priority].append(step)
    return groups


def _extract_agent_results(step_type: str, result: dict) -> dict:
    """提取 Agent 特定的结果字段"""
    extracted = {}

    if step_type == "rag_agent":
        extracted["retrieved_docs"] = result.get("retrieved_docs", [])
        extracted["doc_count"] = len(result.get("retrieved_docs", []))
    elif step_type == "tool_agent":
        extracted["tools_used"] = result.get("tools_used", [])
        extracted["tool_results"] = result.get("tool_results", {})

    return extracted


def _synthesize_results(
        results: dict[str, Any],
        original_query: str,
        state: AgentState
) -> str:
    """综合所有步骤的结果"""
    results_text = _format_results(results)

    prompt = SYNTHESIS_PROMPT.format(
        results=results_text,
        original_query=original_query
    )

    llm = init_chat_model(
        model="gpt-4o-mini",
        model_provider="openai",
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
        temperature=0.3,
    )

    response = llm.invoke([HumanMessage(content=prompt)])

    return response.content


def _format_results(results: dict[str, Any], total_time: float = None) -> str:
    """格式化结果"""
    lines = []

    if total_time:
        lines.append(f"⏱️ **总执行时间**: {total_time:.2f}秒\n")

    lines.append("## 📊 执行结果\n")

    for step_id, result in results.items():
        status = "✅" if result.get("success") else "❌"
        lines.append(f"### {status} {step_id}")
        lines.append(f"- **类型**: {result.get('type', 'unknown')}")

        if result.get("success"):
            lines.append(f"- **状态**: 成功")
            if "execution_time" in result:
                lines.append(f"- **耗时**: {result['execution_time']:.2f}秒")

            # Agent 特定信息
            if result.get("doc_count"):
                lines.append(f"- **检索文档数**: {result['doc_count']}")
            if result.get("tools_used"):
                lines.append(f"- **使用工具**: {', '.join(result['tools_used'])}")

            content = result.get("content", "")
            if content:
                preview = content[:150] + "..." if len(content) > 150 else content
                lines.append(f"- **内容预览**: {preview}")
        else:
            lines.append(f"- **状态**: 失败")
            lines.append(f"- **错误**: {result.get('error', 'Unknown')}")

        lines.append("")

    return "\n".join(lines)