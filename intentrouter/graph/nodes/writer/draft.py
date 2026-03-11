"""
Draft Node - 撰写草稿
"""
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage

from intentrouter import settings
from intentrouter.graph.nodes.writer.outline import _collect_reference_content
from intentrouter.graph.prompts import SECTION_DRAFT_PROMPT
from intentrouter.graph.state import AgentState


def draft_node(state: AgentState) -> dict:
    """
    草稿撰写节点

    流程:
    1. 获取大纲
    2. 逐章节撰写(或并行撰写)
    3. 收集所有章节

    Args:
        state: Agent 状态

    Returns:
        dict: 状态更新
    """
    outline = state.get("outline")

    if not outline:
        return {
            "error": "没有大纲,无法撰写",
            "messages": [AIMessage(content="缺少大纲")]
        }

    sections = outline.get("sections", [])
    document_type = state.get("document_type", "report")
    writing_style = state.get("writing_style", "formal")

    # 收集资料
    reference_content = _collect_reference_content(state)

    # 逐章撰写
    draft_sections = {}
    all_messages = []

    for i, section in enumerate(sections):
        print(f"📝 正在撰写章节 {i + 1}/{len(sections)}: {section['title']}")

        # 获取已完成的章节(作为上下文)
        previous_sections = _format_previous_section(draft_sections)

        # 撰写章节
        section_content = _write_section(
            section=section,
            document_title=outline["title"],
            document_type=document_type,
            writing_style=writing_style,
            reference_content=reference_content,
            previous_sections=previous_sections
        )

        draft_sections[section["id"]] = section_content
        all_messages.append(
            AIMessage(content=f"✅ 完成章节: {section['title']}")
        )

    draft_document = _merge_section(outline["title"], draft_sections)

    return {
        "draft_sections": draft_sections,
        "messages": all_messages + [
            AIMessage(content=f"✅ 草稿完成，共 {len(sections)} 个章节")
        ]
    }


def _write_section(
        section: dict,
        document_title: str,
        document_type: str,
        writing_style: str,
        reference_content: str,
        previous_sections: str
) -> str:
    """撰写单个章节"""
    # 构建Prompt
    prompt = SECTION_DRAFT_PROMPT.format(
        section_title=section["title"],
        section_description=section["description"],
        estimated_words=section.get("estimated_words", 300),
        document_title=document_title,
        document_type=document_type,
        writing_style=writing_style,
        reference_content=reference_content,
        previous_sections=previous_sections
    )

    # 调用 LLM
    llm = init_chat_model(
        model="gpt-4o-mini",
        model_provider="openai",
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
        temperature=0.3,  # 稍微提高创造性
    )

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
    except Exception as e:
        # 失败时返回占位符
        return f"## {section['title']}\n\n（撰写失败: {str(e)}）"


def _format_previous_section(draft_sections: dict[str, str]) -> str:
    """格式化已完成 的章节"""
    if not draft_sections:
        return "（这是第一章）"

    line = ["# 已完成的章节"]
    for section_id, content in draft_sections.items():
        # 只显示前150字
        # TODO 这里是个可优化的点，选择保留哪些内容
        preview = content[:150] + "..." if len(content) > 150 else content
        line.append(f"### {section_id}")
        line.append(preview)

    return "\n".join(line)


def _merge_section(title: str, draft_sections: dict[str, str]) -> str:
    """合并所有章节"""
    lines = [f"# {title}\n"]

    for section_id, content in draft_sections.items():
        lines.append(content)
        lines.append("\n---\n")

    return "\n".join(lines)







