from datetime import datetime

from intentrouter.db.ltm_manager import get_ltm_manager
from intentrouter.graph.state import AgentState
import uuid

from intentrouter.utils.image_utils import validate_image_url


def entry_node(state: AgentState) -> dict:
    """
    入口节点:标准化输入, 初始化状态, 处理附件
    Args:
        state: 当前状态(第一次调用时只有外部传入的字段)
    Returns:
        dict:需要更新到State的字段
    """
    # 1. Thread ID
    if "thread_id" not in state or not state["thread_id"]:
        thread_id = str(uuid.uuid4())
    else:
        thread_id = state["thread_id"]

    # 2. 处理附件（图片)
    attachments = state.get("attachments", []) # 提取附件
    processed_attachments = []

    for attachment in attachments:
        # 验证和标准化附件
        proceed = _process_attachment(attachment)
        if proceed:
            processed_attachments.append(proceed)

    has_multimodal = len(processed_attachments) > 0

    user_context = ""
    user_id = state.get("user_id")
    if user_id:
        user_context = _load_user_memory(user_id)
        if user_context:
            print(f"📋 [Entry Node] 加载用户画像 (user_id={user_id}):\n{user_context}")
        else:
            print(f"ℹ️  [Entry Node] 用户 {user_id} 暂无画像记录")
    else:
        print("⚠️  [Entry Node] 未提供 user_id，跳过用户画像加载")

    return {
        "thread_id": thread_id,
        "user_id": state.get("user_id"),
        "attachments": processed_attachments,
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "source": "api",
            "has_attachments": has_multimodal,
            "attachment_count": len(processed_attachments),
            "user_context": user_context,
        },
        "intent": None,
        "route_decision": None,
        "retrieved_docs": [],
        "tools_used": [],
        "subtask_results": {},
        "error": None,
        "needs_human": False,
    }


def _process_attachment(attachment: dict) -> dict:
    """
    处理单个附件

    Args:
        attachment: 附件信息

    Returns:
        dict: 处理后的附件信息
    """
    # 标准化字段
    url = attachment.get("url") or attachment.get("data")

    if not url:
        print("⚠️ 附件缺少 URL 或 data 字段")
        return None

    # 验证图片 URL
    if not validate_image_url(url):
        print(f"⚠️ 无效的图片 URL: {url[:50]}...")
        return None

    # 返回标准化的附件信息
    return {
        "url": url,
        "type": attachment.get("type", "image"),
        "name": attachment.get("name", "image"),
        "mime_type": attachment.get("mime_type", "image/jpeg")
    }

def _load_user_memory(user_id: str) -> str:
    """
    加载用户的长期记忆
    
    Args:
        user_id: 用户ID
        
    Returns:
        用户画像文本，如果没有记忆则返回空字符串
    """
    try:
        ltm_manager = get_ltm_manager()
        memories = ltm_manager.get_user_memories(user_id, limit=10)

        if not memories:
            return ""

        # 构建用户画像文本
        facts = [m.content for m in memories if m.memory_type == "fact"]
        preference = [m.content for m in memories if m.memory_type == "preference"]
        skills = [m.content for m in memories if m.memory_type == "skill"]

        user_context_parts = []
        if facts:
            # 去重
            unique_facts = list(set(facts))
            user_context_parts.append(f"关于用户的事实: {'; '.join(unique_facts)}")
        if preference:
            unique_prefs = list(set(preference))
            user_context_parts.append(f"用户的偏好: {'; '.join(unique_prefs)}")
        if skills:
            unique_skills = list(set(skills))
            user_context_parts.append(f"用户的技能: {'; '.join(unique_skills)}")

        if not user_context_parts:
            return ""

        user_context = "\n".join(user_context_parts)

        # 更新访问时间
        for memory in memories:
            ltm_manager.update_memory_access(memory.id)

        return user_context

    except Exception as e:
        print(f"⚠️  检索记忆失败: {e}")
        import traceback
        traceback.print_exc()
        return ""









