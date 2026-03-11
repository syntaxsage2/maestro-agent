"""
RAG Agent 节点
"""
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage

from intentrouter.config import settings
from intentrouter.db.vector_store import get_vector_store
from intentrouter.graph.prompts import RAG_ANSWER_PROMPT
from intentrouter.graph.state import AgentState
from intentrouter.graph.utils import build_system_prompt_with_context


def rag_agent_node(state: AgentState):
    """
    RAG Agent 节点: 检索 + 生成

    Args:
        state: 当前状态

    Returns:
        dict: 更新retrieved_docs, messages
    """

    # 1. 获取用户问题
    user_message = ""
    for msg in reversed(state["messages"]):
        if hasattr(msg, "type") and msg.type == "human":
            user_message = msg.content
            break

    if not user_message:
        return {
            "messages": [AIMessage(content="未找到用户问题")],
            "error": "未找到用户问题"
        }

    # 2. 检索相关文档
    vector_store = get_vector_store()
    retrieved_docs = vector_store.similarity_search(
        query=user_message,
        k=4
    )

    if not retrieved_docs:
        return {
            "retrieved_docs": [],
            "messages": [AIMessage(content="抱歉，我在知识库中没有找到相关信息。请尝试换个问法或添加更多背景信息。")]
        }

    # 3.构建上下文
    context = "\n\n".join([f"[文档{i+1}]\n{doc.page_content}" for i, doc in enumerate(retrieved_docs)])

    # 4. 生成答案
    llm = init_chat_model(
        model="gpt-4o-mini",
        model_provider="openai",
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
        temperature=0.3,  # 稍微提高创造性
    )

    prompt = RAG_ANSWER_PROMPT.format(
        context=context,
        question=user_message,
    )

    prompt_with_userMemory = build_system_prompt_with_context(
        base_prompt=prompt,
        state=state,
        include_user_context=True
    )

    response = llm.invoke([
        {"role": "system", "content": "你是一个专业的知识助手,基于提供的文档回答问题"},
        {"role": "user", "content": prompt_with_userMemory}
    ])

    # 5.添加引用来源
    sources = "\n\n---\n**参考来源：**\n"
    for i, doc in enumerate(retrieved_docs):
        source = doc.metadata.get("source", "未知来源")
        sources += f"- 文档{i+1}:{source}\n"

    final_answer = response.content + sources

    return {
        "retrieved_docs": retrieved_docs,
        "messages": [AIMessage(content=final_answer)],
        "context": context[:500],
    }