from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, SystemMessage

from intentrouter.config import settings
from intentrouter.graph.state import AgentState
from intentrouter.graph.utils import build_system_prompt_with_context
from langchain_core.runnables import RunnableConfig


def output_node(state: AgentState, config: RunnableConfig) -> dict:
    """
    输出节点:生成最终回复

    MVP阶段:简单调用LLM回复
    后续: 会根据不同Agent的结果进行格式化
    """
    if state.get("intent") == "general_chat":
        llm = init_chat_model(
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_key='sk-3ad63bc675ff43a7b4195d31fa5b00f4',
            temperature=0.1,
            max_tokens=1024
        )

        # 构建包含用户画像的系统提示
        base_system_prompt = """你是一个友好、专业的AI助手。
            重要提示：
            - 我已经了解用户的背景信息（见下方用户画像）
            - 当用户询问"你知道我是谁吗"、"我的技能是什么"等问题时，请直接使用用户画像中的信息回答
            - 不要说"我不知道"或"您可以告诉我"，而应该根据用户画像给出具体答案
            - 回复要简短、自然，体现出你了解用户
            """
        
        system_prompt = build_system_prompt_with_context(
            base_prompt=base_system_prompt,
            state=state,
            include_user_context=True
        )
        
        # 调试：打印用户上下文和完整系统提示
        user_context = state.get("metadata", {}).get("user_context", "")
        if user_context:
            print(f"📋 [Output Node] 使用用户画像:\n{user_context}")
        else:
            print("⚠️  [Output Node] 没有用户画像")
        
        # 将系统提示添加到消息列表
        messages = [SystemMessage(content=system_prompt)] + state["messages"]
        
        response = llm.invoke(messages, config=config)
        return {
            "messages": [response],
        }

    if state.get("intent") == "simple_qa":
        return {}
    if state.get("intent") == "tool_call":
        return {}
    # 其他意图暂时返回提示信息
    intent = state.get("intent", "unknown")
    message = AIMessage(content=f"[系统]识别到意图:{intent}, 对应Agent开发中...")
    return {"messages": [message]}
