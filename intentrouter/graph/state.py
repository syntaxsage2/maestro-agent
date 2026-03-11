# 定义state
from typing import Optional, Any

from langgraph.graph import MessagesState
from langchain_core.documents import Document


class AgentState(MessagesState):
    # --- 核心字段 （包含messages）---
    thread_id: str  # 区分不同会话
    # ---路由相关字段---
    intent: Optional[str]  # 存储识别意图
    route_decision: Optional[str]  # 路由到哪个Agent
    intent_confidence: float  # 路由决策置信度
    # ---任务规划字段---
    plan: Optional[dict]  # 存储Planner生成的执行计划
    subtask_results: dict[str, Any]  # 存储各个子任务的结果
    # ---检索相关字段---
    retrieved_docs: list[Document]  # Rag Agent 检索到的文档
    context: Optional[str]  # 检索文档的摘要
    # ---工具相关字段---
    tools_used: list[str]  # 记录使用了那些工具
    tool_results: dict[str, Any]  # 工具执行结果
    # ---多模态相关字段---
    attachments: list[dict]  # 存储上传的图片元信息
    multimodal_analysis: Optional[dict]  # 分析结果
    # ---元数据字段---
    user_id: Optional[str]  # 关联用户
    metadata: dict[str, Any]  # 杂项信息
    error: Optional[str]  # 错误信息(节点执行失败时填充)
    needs_human: bool  # 是否需要人工介入
    # === Writer 相关字段 ===
    document_type: Optional[str]  # 文档类型：report, email, blog, weekly_report
    outline: Optional[dict]  # 文档大纲
    draft_sections: dict[str, str]  # 草稿章节 {section_id: content}
    final_document: Optional[str]  # 最终文档
    writing_style: Optional[str]  # 写作风格：formal, casual, technical
    # === HITL 相关字段 ===
    interrupt_reason: Optional[str]  # 中断原因
    human_feedback: Optional[dict]  # 人工反馈
    interrupt_data: Optional[dict]  # 中断时的数据（供用户审核）
    # === Tool Agent 循环字段 ===
    tool_iteration: int  # Tool Agent 循环计数（防止无限循环）


