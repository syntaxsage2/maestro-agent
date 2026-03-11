"""
Human-in-the-Loop (HITL) 相关路由
"""
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from intentrouter.graph.main_graph import create_graph

router = APIRouter(prefix="/hitl", tags=["HITL"])

# 复用 graph 实例
_graph = None


async def get_graph():
    global _graph
    if _graph is None:
        _graph = await create_graph()
    return _graph


# ===== Schemas =====

class InterruptStatus(BaseModel):
    """中断状态"""
    is_interrupted: bool = Field(..., description="是否处于中断状态")
    thread_id: str = Field(..., description="会话ID")
    next_node: Optional[str] = Field(None, description="下一个要执行的节点")
    interrupt_reason: Optional[str] = Field(None, description="中断原因")
    tool_calls: Optional[list] = Field(None, description="待确认的工具调用")
    state_exists: bool = Field(True, description="会话状态是否存在（用于区分'还未初始化'和'已完成'）")


class HumanFeedback(BaseModel):
    """人工反馈"""
    decision: str = Field(..., description="决策: approve, reject, modify")
    reason: Optional[str] = Field(None, description="决策原因")
    modified_data: Optional[dict] = Field(None, description="修改后的数据（仅 modify 时）")

    class Config:
        json_schema_extra = {
            "example": {
                "decision": "approve",
                "reason": "已确认，可以执行"
            }
        }


class ResumeRequest(BaseModel):
    """恢复执行请求"""
    thread_id: str = Field(..., description="会话ID")
    feedback: HumanFeedback = Field(..., description="人工反馈")

    class Config:
        json_schema_extra = {
            "example": {
                "thread_id": "abc-123",
                "feedback": {
                    "decision": "approve",
                    "reason": "已确认"
                }
            }
        }


class ResumeResponse(BaseModel):
    """恢复执行响应"""
    thread_id: str
    message: str
    status: str  # completed, interrupted, error


# ===== 路由 =====

@router.get("/status/{thread_id}", response_model=InterruptStatus)
async def get_interrupt_status(thread_id: str):
    """
    获取会话的中断状态

    Args:
        thread_id: 会话ID

    Returns:
        InterruptStatus: 中断状态信息
        
    说明:
        - 始终返回200状态码，通过 state_exists 字段区分会话状态
        - state_exists=False: 会话还未初始化或已被删除，前端应继续轮询或停止
        - state_exists=True: 会话存在，通过 is_interrupted 判断是否需要人工确认
    """
    try:
        app = await get_graph()
        config = {"configurable": {"thread_id": thread_id}}

        # 获取状态
        state = await app.aget_state(config)

        # 会话不存在或还未初始化：返回 state_exists=False，is_interrupted=False
        if not state.values:
            return InterruptStatus(
                is_interrupted=False,
                thread_id=thread_id,
                next_node=None,
                interrupt_reason=None,
                tool_calls=None,
                state_exists=False  # 关键：明确告诉前端状态不存在
            )

        # 会话存在：检查是否中断
        is_interrupted = bool(state.next)
        next_node = state.next[0] if state.next else None

        # 提取中断信息
        interrupt_reason = None
        tool_calls = None

        if state.tasks:
            for task in state.tasks:
                if hasattr(task, 'interrupts') and task.interrupts:
                    interrupt_value = task.interrupts[0].value
                    interrupt_reason = interrupt_value.get("reason")
                    tool_calls = interrupt_value.get("tool_calls")
                    break

        return InterruptStatus(
            is_interrupted=is_interrupted,
            thread_id=thread_id,
            next_node=next_node,
            interrupt_reason=interrupt_reason,
            tool_calls=tool_calls,
            state_exists=True  # 状态存在
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")


@router.post("/resume", response_model=ResumeResponse)
async def resume_execution(request: ResumeRequest):
    """
    恢复中断的执行

    流程：
    1. 检查会话是否处于中断状态
    2. 更新 human_feedback
    3. 继续执行

    Args:
        request: 恢复请求

    Returns:
        ResumeResponse: 执行结果
    """
    try:
        app = await get_graph()
        config = {"configurable": {"thread_id": request.thread_id}}

        # 1. 检查状态
        state = await app.aget_state(config)
        if not state.values:
            raise HTTPException(status_code=404, detail="会话不存在")

        if not state.next:
            raise HTTPException(status_code=400, detail="会话未处于中断状态")

        # 2. 更新状态
        await app.aupdate_state(
            config=config,
            values={"human_feedback": request.feedback.model_dump()}
        )

        # 3. 继续执行
        result = await app.ainvoke(None, config=config)

        # 4. 检查执行结果
        final_state = await app.aget_state(config)
        status = "interrupted" if final_state.next else "completed"

        # 提取最终消息
        messages = result.get("messages", [])
        final_message = messages[-1].content if messages else "执行完成"

        return ResumeResponse(
            thread_id=request.thread_id,
            message=final_message,
            status=status
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"恢复执行失败: {str(e)}")


@router.post("/reject/{thread_id}")
async def reject_operation(
    thread_id: str,
    reason: Optional[str] = None
):
    """
    快捷拒绝操作

    Args:
        thread_id: 会话ID
        reason: 拒绝原因

    Returns:
        执行结果
    """
    request = ResumeRequest(
        thread_id=thread_id,
        feedback=HumanFeedback(
            decision="reject",
            reason=reason or "用户拒绝"
        )
    )
    return await resume_execution(request)


@router.post("/approve/{thread_id}")
async def approve_operation(
    thread_id: str,
    reason: Optional[str] = None
):
    """
    快捷批准操作

    Args:
        thread_id: 会话ID
        reason: 批准原因

    Returns:
        执行结果
    """
    request = ResumeRequest(
        thread_id=thread_id,
        feedback=HumanFeedback(
            decision="approve",
            reason=reason or "用户批准"
        )
    )
    return await resume_execution(request)

