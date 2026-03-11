"""
Planner 节点-任务分解与规划
"""
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langsmith import traceable

from intentrouter.config import settings
from intentrouter.graph.prompts import PLANNER_PROMPT
from intentrouter.graph.state import AgentState


# 为关键函数添加追踪
@traceable(name="planner_node", run_type="chain")
def planner_node(state: AgentState) -> dict:
    """
    Planner 节点 - 将复杂任务分解为子任务

    流程:
    1. 提取用户任务
    2. 使用LLM生成执行计划
    3. 解析并验证计划
    4. 存入state.plan

    Args:
        state: Agent 状态

    Returns:
        dict: 状态更新
    """
    # 1.获取用户任务
    user_message = state["messages"][-1].content

    # 2. 构建prompt
    parser = JsonOutputParser()
    format_instructions = parser.get_format_instructions()
    prompt_tmpl = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{user_prompt}\n\n{format_instructions}")
    ]).partial(format_instructions=format_instructions)

    user_prompt = PLANNER_PROMPT.format(user_task=user_message)

    # 3.调用LLM生成计划
    llm = init_chat_model(
        model="gpt-4o-mini",
        model_provider="openai",
        base_url=settings.openai_base_url,
        api_key=settings.openai_api_key,
        temperature=0.3,  # 稍微提高创造性
    )

    try:
        chain = prompt_tmpl | llm | parser
        plan = chain.invoke({"user_prompt": user_prompt})

        # 验证计划格式
        if not _validate_plan(plan):
            raise ValueError("计划无效")

        # 4.返回状态更新
        return {
            "plan": plan,
            "messages": [
                AIMessage(
                    content=f"已生成执行计划\n\n"
                            f"**任务**:{plan['task_summary']}\n"
                            f"**步骤数**: {len(plan['steps'])}\n"
                            f"**预估耗时**: {plan.get('estimated_time', '未知')}\n\n"
                            f"开始执行..."
                )
            ]
        }
    except Exception as e:
        # 计划生成失败，回退到简单模式
        return {
            "plan": None,
            "error": f"任务规划失败: {str(e)}",
            "messages": [
                AIMessage(
                    content=f"❌ 任务规划失败: {str(e)}\n\n"
                            f"我将尝试直接回答您的问题。"
                )
            ]
        }


def _validate_plan(plan: dict) -> bool:
    """
    验证计划格式是否正确

    Args:
        plan: 计划字典

    Returns:
        bool: 是否有效
    """
    """
    [{'id': 'step_1', 'type': 'tool_agent', 'goal': '搜索关于 LangGraph 的最新信息', 'parameters': {}, 
    'depends_on': [], 'priority': 1}, {'id': 'step_2', 'type': 'rag_agent', 'goal': '从知识库检索关于 LangGraph 的文档', 
    'parameters': {}, 'depends_on': ['step_1'], 'priority': 2}, {'id': 'step_3', 'type': 'synthesis', 
    'goal': '综合搜索结果和知识库信息生成技术总结', 'parameters': {}, 'depends_on': ['step_1', 'step_2'], 'priority': 3}]
    """
    # 检查必需字段
    if "steps" not in plan:
        return False

    if not isinstance(plan["steps"], list):
        return False

    # 检查每个步骤
    for step in plan["steps"]:
        # 必要字段
        required_fields = ["id", "type", "goal", "priority"]
        if not all(field in step for field in required_fields):
            return False

        # 类型检查
        if step["type"] not in ["rag_agent", "tool_agent", "synthesis"]:
            return False

        if "depends_on" in step and not isinstance(step["depends_on"], list):
            return False

    return True
