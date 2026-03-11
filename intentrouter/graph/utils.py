"""
Graph 工具函数
"""
from typing import Optional
from intentrouter.graph.state import AgentState


def build_system_prompt_with_context(
    base_prompt: str,
    state: AgentState,
    include_user_context: bool = True
) -> str:
    """
    构建包含用户画像的系统提示词

    Args:
        base_prompt: 基础系统提示词
        state: 当前状态
        include_user_context: 是否包含用户画像

    Returns:
        完整的系统提示词

    Example:
        >> base = "你是一个助手"
        >> state = {"metadata": {"user_context": "用户是Python开发者"}}
        >> prompt = build_system_prompt_with_context(base, state)
        >> print(prompt)
        你是一个助手

        ## 📋 关于当前用户
        用户是Python开发者

        请利用上述用户信息来提供个性化、精准的回答。
    """
    prompt = base_prompt

    if include_user_context:
        user_context = state.get("metadata", {}).get("user_context", "")
        if user_context:
            prompt += f"\n\n## 📋 关于当前用户\n{user_context}\n\n**请利用上述用户信息来提供个性化、精准的回答。当用户询问关于自己的信息时，请直接引用上述内容。**"

    return prompt


def get_user_context(state: AgentState) -> Optional[str]:
    """
    从 State 中获取用户画像

    Args:
        state: 当前状态

    Returns:
        用户画像文本，如果没有则返回 None

    Example:
        >> state = {"metadata": {"user_context": "用户是Python开发者"}}
        >> context = get_user_context(state)
        >> print(context)
        用户是Python开发者
    """
    return state.get("metadata", {}).get("user_context")


def has_user_context(state: AgentState) -> bool:
    """
    检查是否有用户画像

    Args:
        state: 当前状态

    Returns:
        如果有用户画像返回 True，否则返回 False
    """
    user_context = get_user_context(state)
    return user_context is not None and len(user_context.strip()) > 0

