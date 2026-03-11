"""
refine Node - 润色文档
"""
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage

from intentrouter import settings
from intentrouter.graph.nodes.writer.draft import _merge_section
from intentrouter.graph.prompts import REFINE_DOCUMENT_PROMPT
from intentrouter.graph.state import AgentState
from intentrouter.templates.documents import create_document_template


def refine_node(state: AgentState) -> dict:
    """
    文档润色节点:

    流程:
    1. 获取草稿
    2. 使用LLM 润色
    3. 应用文档模板格式化
    4. 生成最终文档

     Args:
        state: Agent 状态

    Returns:
        dict: 状态更新
    """
    draft_sections = state.get("draft_sections", {})
    outline = state.get("outline")
    document_type = state.get("document_type", "report")

    if not draft_sections:
        return {
            "error": "没有草稿，无法润色",
            "messages": [AIMessage(content="❌ 缺少草稿")]
        }

    # 1. 合并草稿
    draft_document = _merge_section(outline["title"], draft_sections)

    # 2. 使用LLM润色
    refined_content = _refine_document(draft_document, document_type)

    # 3. 应用文档模板
    final_document = _apply_template(
        document_type=document_type,
        title=outline["title"],
        refined_content=refined_content,
        draft_sections=draft_sections
    )

    # 4. 统计信息
    word_count = len(final_document)
    section_count = len(draft_sections)

    return {
        "final_document": final_document,
        "messages": [
            AIMessage(
                content=f"✅ 文档已完成！\n\n"
                        f"**标题**: {outline['title']}\n"
                        f"**类型**: {document_type}\n"
                        f"**章节数**: {section_count}\n"
                        f"**字数**: {word_count}\n\n"
                        f"---\n\n{final_document}"
            )
        ]
    }


def _refine_document(draft_document: str, document_type: str) -> str:
    """使用 LLM 润色文档"""
    prompt = REFINE_DOCUMENT_PROMPT.format(
        draft_document=draft_document,
        document_type=document_type
    )

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
        print(f"⚠️ 润色失败，返回原始草稿: {e}")
        return draft_document


def _apply_template(
    document_type: str,
    title: str,
    refined_content: str,
    draft_sections: dict[str, str]
) -> str:
    """应用文档模板"""
    try:
        # 尝试将refined_content 按章节分割
        # 如果LLM保持章节结构，我们可以提取
        sections_dict = _extract_sections_from_refined(refined_content, draft_sections)

        # 创建并渲染模板
        template = create_document_template(document_type, title, sections_dict)
        return template.render()

    except Exception as e:
        print(f"⚠️ 模板应用失败，返回润色内容: {e}")
        return refined_content


def _extract_sections_from_refined(
        refined_content: str,
        original_sections: dict[str, str]
) -> dict[str, str]:
    """从润色后的内容中提取章节"""
    # 简单实现：按 "##" 分割
    sections = {}
    current_section = []
    section_id = "section_1"

    for line in refined_content.split("\n"):
        if line.startswith("##"):
            # 保存前一个章节
            if current_section:
                sections[section_id] = "\n".join(current_section)
                # 递增 section_id
                num = int(section_id.split("_")[1])
                section_id = f"section_{num + 1}"
            current_section = [line]
        else:
            current_section.append(line)

    # 保存最后一个章节
    if current_section:
        sections[section_id] = "\n".join(current_section)

    # 如果提取失败，使用原始章节
    if not sections:
        sections = original_sections

    return sections



















