"""
Outline Node - 生产文档大纲
"""
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

from intentrouter import settings
from intentrouter.graph.prompts import OUTLINE_GENERATION_PROMPT, DOCUMENT_TYPE_CONFIG
from intentrouter.graph.state import AgentState


def outline_node(state: AgentState) -> dict:
    """
    大纲生成节点

    流程:
    1. 提取用户需求和文档类型
    2. 收集参考资料(如果有)
    3. 使用LLM生成大纲
    4. 解析并验证大纲

     Args:
        state: Agent 状态

    Returns:
        dict: 状态更新
    """

    # 1. 提取信息
    user_message = state["messages"][-1].content
    document_type = state.get("document_type", "report")

    # 2. 收集参考资料
    reference_content = _collect_reference_content(state)

    # 构建prompt
    parser = JsonOutputParser()
    format_instructions = parser.get_format_instructions()
    prompt_tmpl = ChatPromptTemplate.from_messages([
        ("human", "{user_prompt} \n\n {format_instructions}")
    ]).partial(format_instructions=format_instructions)

    user_prompt = OUTLINE_GENERATION_PROMPT.format(
        user_request=user_message,
        document_type=document_type,
        reference_content=reference_content,
    )

    # 4. 调用LLM生成大纲
    llm = init_chat_model(
        model="gpt-4o-mini",
        model_provider="openai",
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
        temperature=0.3,  # 稍微提高创造性
    )

    try:
        chain = prompt_tmpl | llm | parser
        outline = chain.invoke({"user_prompt": user_prompt})

        # 验证
        if not _validate_outline(outline):
            raise ValueError("大纲格式无效")

        # 5. 格式化大纲摘要
        outline_summary = _format_outline_summary(outline)

        return {
            "outline": outline,
            "document_type": outline.get("document_type", document_type),
            "writing_style": outline.get("writing_style", "formal"),
            "messages": [AIMessage(content=f"✅ 大纲已生成\n\n{outline_summary}")]
        }

    except Exception as e:
        # 生成失败,使用默认大纲
        default_outline = _create_default_outline(user_message, document_type)

        return {
            "outline": default_outline,
            "document_type": document_type,
            "error": f"大纲生成失败，使用默认模板: {str(e)}",
            "messages": [AIMessage(content="⚠️ 使用默认大纲模板")]
        }


def _collect_reference_content(state: AgentState) -> str:
    """收集参考资料"""
    references = []

    # 从 RAG 结果收集
    retrieved_docs = state.get("retrieved_docs", [])
    if retrieved_docs:
        references.append("## RAG 检索结果：")
        for i, doc in enumerate(retrieved_docs[:3], 1):  # 最多 3 个
            references.append(f"{i}. {doc.page_content[:200]}...")

    # 从工具调用结果收集
    tool_results = state.get("tool_results", {})
    if tool_results:
        references.append("\n## 工具调用结果：")
        for tool_name, result in tool_results.items():
            if result.get("success"):
                content = str(result.get("result", ""))[:200]
                references.append(f"- {tool_name}: {content}...")

    # 从子任务结果收集
    subtask_results = state.get("subtask_results", {})
    if subtask_results:
        references.append("\n## 子任务结果：")
        for step_id, result in subtask_results.items():
            if result.get("success"):
                content = result.get("content", "")[:200]
                references.append(f"- {step_id}: {content}...")

    return "\n".join(references) if references else "无参考资料"


def _validate_outline(outline: dict) -> bool:
    """验证大纲"""
    required_fields = ["title", "section"]
    if not all(field in outline for field in required_fields):
        return False

    if not isinstance(outline["sections"], list) or len(outline["sections"]) == 0:
        return False

        # 验证每个章节
    for section in outline["sections"]:
        if not all(field in section for field in ["id", "title", "description"]):
            return False

    return True


def _format_outline_summary(outline: dict) -> str:
    """格式化大纲摘要"""
    lines = [
        f"**标题**: {outline['title']}",
        f"**章节数**: {len(outline['sections'])}",
        f"**预估字数**: {outline.get('total_estimated_words', 'N/A')}",
        "",
        "**章节列表**:"
    ]

    for i, section in enumerate(outline["sections"], 1):
        lines.append(f"{i}. {section['title']}")
        lines.append(f"   - {section['description']}")

    return "\n".join(lines)


def _create_default_outline(user_request: str, document_type: str) -> dict:
    """创建默认大纲"""
    config = DOCUMENT_TYPE_CONFIG.get(document_type, DOCUMENT_TYPE_CONFIG["report"])

    sections = []
    for i, section_title in enumerate(config["structure"], 1):
        sections.append({
            "id": f"section_{i}",
            "title": section_title,
            "description": f"{section_title}相关内容",
            "estimated_words": config["typical_length"] // len(config["structure"])
        })

    return {
        "title": user_request[:50],
        "document_type": document_type,
        "sections": sections,
        "writing_style": config["style"]
    }
