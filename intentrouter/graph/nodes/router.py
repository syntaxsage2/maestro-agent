import json
from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.chat_models import init_chat_model

from intentrouter.graph.state import AgentState
from intentrouter.config import settings
from intentrouter.graph.utils import build_system_prompt_with_context
from intentrouter.graph.prompts import INTENT_CLASSIFICATION_PROMPT


def intent_router_node(state: AgentState) -> dict:
    """
    意图路由节点:识别用户意图并决定路由

    Args:
        state:当前状态

    Returns:
        dict: 更新 intent, intent_confidence, route_decision
    """
    # 1.获取用户消息
    user_message = get_last_user_message(state)

    # ===========多模态检测=============
    attachments = state.get("attachments", [])
    has_images = len(attachments) > 0

    if has_images:
        return {
            "intent": "multimodal",
            "route_decision": "vision_agent",
            "intent_confidence": 1.0,
            "messages": [AIMessage(content=f"检测到图片输入，正在分析...")]
        }

    if not user_message:
        # 没有用户消息，默认闲聊
        return {
            "intent": "general_chat",
            "intent_confidence": 1.0,
            "route_decision": "output",
        }



    # 2.获取用户意图
    result = classify_intent(user_message, state)

    # 3. 决定路由
    route = decide_route(result["intent"])

    return {
        "intent": result["intent"],
        "intent_confidence": result.get("confidence", 0.0),
        "route_decision": route,
        "metadata": {
            **state.get("metadata", {}),
            "intent_reasoning": result.get("reasoning", "")
        }
    }


def get_last_user_message(state: AgentState) -> str:
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            return msg.content
    return ""


def classify_intent(user_message: str, state) -> dict:
    llm = init_chat_model(
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
        api_key='sk-3ad63bc675ff43a7b4195d31fa5b00f4',
        temperature=0.1,
        max_tokens=1024
    )

    # Prompt
    INTENT_CLASSIFICATION_PROMPT = """你是一个意图识别专家。分析用户消息，判断其意图类型。

    可选的意图类型：
    1. simple_qa - 简单问答、知识查询（单轮对话即可解决）
    2. complex_task - 复杂任务（需要多步骤、调用多个工具）
    3. tool_call - 需要调用外部工具/API（发邮件、查数据库、文件操作等）
    4. general_chat - 普通闲聊、打招呼、致谢
    5. generation - 文档生成 (需要撰写,生成长文档,报告,邮件等)

    示例：
    - "Python 的 asyncio 怎么用？" → simple_qa
    - "分析这3个PDF并生成周报，发给领导" → complex_task
    - "帮我发邮件给张三" → tool_call
    - "你好" / "谢谢" → general_chat
    - "写一份关于 LangGraph 的技术报告" / "帮我写一封感谢邮件" / "写一篇博客介绍 RAG" → writer_agent

    用户消息：{user_message}

    请以 JSON 格式返回：
    {{
        "intent": "意图类型",
        "confidence": 0.95,
        "reasoning": "简短的判断理由"
    }}
    
    注意:
    "confidence": 0.95(正确)
    "confidence": 0. ninety-five(错误!!!!!!!)
    当用户询问与自身相关的信息（如：我的名字是什么、我之前说过什么、我是谁等），无论是否有相关数据，均将意图归类为"general_chat"（chat），而非"知识查询"或其他类型。
    你要区分简单问答,知识查询 与 调用外部工具的关系, 我问个时间或者天气,这种问题是输出要调用工具或者API的
    """

    prompt = INTENT_CLASSIFICATION_PROMPT.format(user_message=user_message)

    system_prompt = build_system_prompt_with_context(
        base_prompt=prompt,
        state=state,
        include_user_context=True
    )

    response = llm.invoke([
        SystemMessage(content="你是意图识别助手,必须返回JSON格式"),
        HumanMessage(content=system_prompt)
    ])
    print("111", response)
    # 解析JSON
    # TODO 不能只让LLM回答JSON格式，自己需要格式化
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        result = json.loads(content)
        return result
    except json.JSONDecodeError as e:
        print(f"JSON Parsing Error: {e}, content: {response.content}")
        return {
            "intent": "general_chat",
            "confidence": 0.5,
            "reasoning": "解析失败，使用默认意图"
        }


def decide_route(intent: str) -> str:
    route_map = {
        "simple_qa": "rag_agent",  # 简单问答 → RAG
        "complex_task": "planner",  # 复杂任务 → Planner
        "tool_call": "tool_agent",  # 工具调用 → Tool Agent
        "general_chat": "output",  # 闲聊 → 直接输出
        "generation": "writer_agent",  # 生成 -> 写作
    }
    return route_map.get(intent, "output")  # 默认路由到 output