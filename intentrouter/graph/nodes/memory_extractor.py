"""
记忆提取节点
从对话中提取值得长期记住的信息
"""
from typing import Any, Dict

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from intentrouter.config import settings
from intentrouter.db.ltm_manager import get_ltm_manager
from intentrouter.graph.prompts import MEMORY_EXTRACTION_PROMPT
from intentrouter.graph.state import AgentState


def memory_extractor_node(state: AgentState) -> Dict[str, Any]:
    """
    记忆提取节点

    从最后几轮对话中提取值得记住的信息并保存
    """
    user_id = state.get("user_id")
    if user_id is None:
        print("⚠️  没有user_id，跳过记忆提取")
        return {}

    # 获取最近的对话(最后两轮)
    messages = state.get("messages", [])
    if len(messages) < 2:
        # 对话太短
        return {}

    recent_messages = messages[-4:]

    # 构建对话历史文本
    conversation = "\n".join([
        f"{msg.type}: {msg.content}"
        for msg in recent_messages
    ])

    parser = JsonOutputParser()

    prompt = ChatPromptTemplate.from_messages([
        ("system", MEMORY_EXTRACTION_PROMPT),
        ("human", "请从以下对话中提取记忆：\n{conversation}")
    ])

    # 调用LLM提取记忆 - 使用与router相同的配置
    from langchain.chat_models import init_chat_model
    from intentrouter.graph.utils import build_system_prompt_with_context

    llm = init_chat_model(
        model="gpt-4.1-nano",  # 与router保持一致
        model_provider="openai",
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
        temperature=0,
    )

    try:
        chain = prompt | llm | parser
        result = chain.invoke({"conversation": conversation})

        memories = result.get("memories", [])

        if not memories or len(memories) == 0:
            # 没有值得记住的新信息
            print(f"ℹ️  没有找到需要提取的记忆")
            return {}

        # 保存记忆到数据库
        ltm_manager = get_ltm_manager()
        saved_count = 0

        for memory in memories:
            try:
                memory_type = memory.get("type")
                content = memory.get("content")
                importance = memory.get("importance", 0.5)

                if memory_type in ["fact", "preference", "skill"] and content and content.strip():
                    ltm_manager.add_memory(
                        user_id=user_id,
                        memory_type=memory_type,
                        content=content.strip(),
                        importance=importance
                    )
                    saved_count += 1
                    print(f"💾 保存记忆: {memory_type} - {content[:50]}...")
            except Exception as mem_error:
                print(f"⚠️  保存单条记忆失败: {mem_error}")
                continue

        if saved_count > 0:
            print(f"✓ 共保存 {saved_count} 条记忆")
        else:
            print(f"ℹ️  没有成功保存任何记忆")

    except Exception as e:
        print(f"❌ 记忆提取过程中失败: {e}")
        import traceback
        traceback.print_exc()
        # 不抛出异常，避免影响主流程
        pass

    # 始终返回空字典，确保流程正常结束
    return {}




