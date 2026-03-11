"""
Tool Agent 节点 - 拆分为两个节点以支持中断
"""
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langgraph.errors import NodeInterrupt
from langgraph.prebuilt import ToolNode

from intentrouter.config import settings
from intentrouter.graph.state import AgentState
from intentrouter.tools.registry import tools_registry

from langchain_core.runnables import RunnableConfig

import intentrouter.tools


def _get_llm_with_tools():
    """获取带工具的 LLM（复用逻辑）"""
    # 1. 懒加载 MCP 工具
    if not tools_registry.is_mcp_loaded():
        print("🔄 检测到 MCP 工具未加载，正在加载...")
        try:
            import asyncio
            from intentrouter.tools.builtin import register_mcp_tools
            asyncio.run(register_mcp_tools())
            print(f"✅ MCP 工具加载完成，当前共有 {len(tools_registry.list_tools())} 个工具")
        except Exception as e:
            print(f"⚠️ MCP 工具加载失败: {e}")

    # 2. 获取工具
    tools = tools_registry.get_all_tools()
    if not tools:
        return None, None

    # 3. 创建 LLM
    llm = init_chat_model(
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
        api_key='sk-3ad63bc675ff43a7b4195d31fa5b00f4',
        temperature=0.1,
        max_tokens=1024
    )

    return llm, llm.bind_tools(tools=tools)


def tool_call_node(state: AgentState, config: RunnableConfig):
    """
    Tool Call 节点：生成工具调用（ReAct 循环）
    
    这个节点负责：
    1. 调用 LLM 生成工具调用
    2. 返回 AIMessage（包含 tool_calls）
    3. 如果不需要工具，返回最终回复
    
    ⚠️ 不在这里执行工具！执行在 tool_execute_node
    """
    # 1. 获取 LLM
    llm, llm_with_tools = _get_llm_with_tools()
    if not llm_with_tools:
        return {
            "messages": [AIMessage(content="没有可用的工具")],
            "error": "No tools available"
        }

    # 2. 调用 LLM（ReAct 循环）
    messages = state["messages"]
    max_iterations = state.get("tool_iteration", 0)

    # 防止无限循环
    if max_iterations >= 10:
        return {
            "messages": [AIMessage(content="抱歉，任务过于复杂，已达到最大尝试次数。")],
            "tool_iteration": 0  # 重置
        }

    print(f"\n🔄 Tool Agent 第 {max_iterations + 1} 轮...")

    # 3. 调用 LLM 生成工具调用
    from langchain_core.messages import SystemMessage
    system_prompt = SystemMessage(content=(
        "你是一个专门负责调用工具的智能助手。你已经绑定了一系列外部工具（如获取天气、时间、计算等）。\n"
        "1. 当用户的请求需要外部数据支持时，你**必须**调用相应的工具，绝不能编造数据或直接回复“我不知道”/“我无法获取”。\n"
        "2. 不要直接回答天气、时间、数学计算等能通过工具获得的问题，必须生成 tool_calls 返回。\n"
        "3. 如果已经有了工具执行结果，请总结并回答用户的问题。"
    ))
    
    # 构造新的消息列表，将系统提示词放在首位
    messages_with_sys = [system_prompt] + messages
    response = llm_with_tools.invoke(messages_with_sys, config=config)

    # 4. 返回 response（会被保存到 checkpoint）
    return {
        "messages": [response],
        "tool_iteration": max_iterations + 1
    }


def tool_execute_node(state: AgentState):
    """
    Tool Execute 节点：执行工具
    
    这个节点负责：
    1. 检查最后一条消息是否有 tool_calls
    2. 执行工具
    3. 返回工具结果
    """
    messages = state["messages"]
    last_message = messages[-1]

    # 1. 检查是否有工具调用
    if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
        # 没有工具调用，结束
        return {
            "tool_iteration": 0  # 重置迭代计数
        }

    # 2. 检查是否需要人工审批（仅第一次）
    human_feedback = state.get("human_feedback")
    if not human_feedback:
        tool_calls = last_message.tool_calls
        high_risk_tools = ["delete_file", "send_email", "execute_code"]
        has_high_risk = any(tc["name"] in high_risk_tools for tc in tool_calls)

        if has_high_risk:
            print("⚠️ 检测到高风险操作，需要人工确认")
            interrupt_data = {
                "reason": "高风险工具调用需要确认",
                "tool_calls": [
                    {
                        "name": tc["name"],
                        "args": tc["args"],
                        "id": tc.get("id", ""),
                    }
                    for tc in tool_calls
                ],
                "thread_id": state.get("thread_id")
            }
            raise NodeInterrupt(value=interrupt_data)

    # 3. 用户已批准或非高风险，执行工具
    if human_feedback:
        decision = human_feedback.get("decision")
        if decision == "reject":
            return {
                "messages": [AIMessage(content=f"❌ 操作已被用户拒绝\n\n原因：{human_feedback.get('reason', '无')}")],
                "human_feedback": None,
                "tool_iteration": 0
            }
        elif decision == "modify":
            print(f"✏️ 用户修改了参数：{human_feedback.get('modified_data', {})}")
        # approve 或 modify 都继续执行

    print(f"🔧 执行工具: {[tc['name'] for tc in last_message.tool_calls]}")

    # 4. 执行工具
    tools = tools_registry.get_all_tools()
    tool_node = ToolNode(tools)
    tool_result = tool_node.invoke({"messages": [last_message]})

    # 5. 返回工具结果
    return {
        "messages": tool_result["messages"],
        "tools_used": [tc["name"] for tc in last_message.tool_calls],
        "human_feedback": None  # 清空反馈
    }


