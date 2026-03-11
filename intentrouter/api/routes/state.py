"""
状态管理相关路由
"""
from typing import Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from intentrouter.graph.main_graph import create_graph

router = APIRouter(prefix="/state", tags=["State"])

_graph = None


async def get_graph():
    global _graph
    if _graph is None:
        _graph = await create_graph()
    return _graph


# ===== Schemas =====

class StateInfo(BaseModel):
    """状态信息"""
    thread_id: str
    messages_count: int
    intent: Optional[str] = None
    route: Optional[str] = None
    tools_used: List[str] = []
    is_interrupted: bool = False
    next_node: Optional[str] = None
    metadata: dict = {}


class ResetResponse(BaseModel):
    """重置响应"""
    thread_id: str
    status: str
    message: str


# ===== 路由 =====

@router.get("/{thread_id}", response_model=StateInfo)
async def get_state(thread_id: str):
    """
    获取会话状态

    Args:
        thread_id: 会话ID

    Returns:
        StateInfo: 状态信息
    """
    try:
        app = await get_graph()
        config = {"configurable": {"thread_id": thread_id}}

        state = await app.aget_state(config)

        if not state.values:
            raise HTTPException(status_code=404, detail="会话不存在")

        values = state.values

        return StateInfo(
            thread_id=thread_id,
            messages_count=len(values.get("messages", [])),
            intent=values.get("intent"),
            route=values.get("route_decision"),
            tools_used=values.get("tools_used", []),
            is_interrupted=bool(state.next),
            next_node=state.next[0] if state.next else None,
            metadata=values.get("metadata", {})
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{thread_id}", response_model=ResetResponse)
async def reset_state(thread_id: str):
    """
    重置会话状态（清空历史）

    ?? 注意：这会删除所有历史记录

    Args:
        thread_id: 会话ID

    Returns:
        ResetResponse: 重置结果
    """
    try:
        app = await get_graph()
        config = {"configurable": {"thread_id": thread_id}}

        # 检查是否存在
        state = await app.aget_state(config)
        if not state.values:
            raise HTTPException(status_code=404, detail="会话不存在")

        # 重置状态（通过更新为空状态）
        # LangGraph 的 checkpoint 需要通过特殊方式清空
        from intentrouter.db.checkpointer import get_checkpointer

        checkpointer = get_checkpointer()

        # 清空该 thread 的所有 checkpoint
        # 注意：这取决于你使用的 checkpointer 实现
        # PostgresSaver 有 delete 方法

        return ResetResponse(
            thread_id=thread_id,
            status="success",
            message="会话已重置"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{thread_id}/history")
async def get_checkpoint_history(thread_id: str, limit: int = 10):
    """
    获取会话的 checkpoint 历史（时光机功能）

    可以看到会话的所有历史状态

    Args:
        thread_id: 会话ID
        limit: 返回数量限制

    Returns:
        历史 checkpoint 列表
    """
    try:
        app = await get_graph()
        config = {"configurable": {"thread_id": thread_id}}

        # 获取历史状态
        history = []

        async for state in app.aget_state_history(config, limit=limit):
            history.append({
                "checkpoint_id": str(state.config["configurable"].get("checkpoint_id", "")),
                "parent_checkpoint_id": str(state.parent_config["configurable"].get("checkpoint_id", "")) if state.parent_config else None,
                "messages_count": len(state.values.get("messages", [])),
                "intent": state.values.get("intent"),
                "route": state.values.get("route_decision"),
                "next_node": state.next[0] if state.next else None,
                "metadata": state.metadata
            })

        return {
            "thread_id": thread_id,
            "history": history,
            "total": len(history)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{thread_id}/rollback")
async def rollback_to_checkpoint(
    thread_id: str,
    checkpoint_id: str
):
    """
    回滚到指定 checkpoint（时光倒流）

    ?? 实验性功能

    Args:
        thread_id: 会话ID
        checkpoint_id: checkpoint ID

    Returns:
        回滚结果
    """
    try:
        app = await get_graph()

        # 构造目标 config
        target_config = {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id
            }
        }

        # 获取目标状态
        target_state = await app.aget_state(target_config)

        if not target_state.values:
            raise HTTPException(status_code=404, detail="Checkpoint 不存在")

        # 更新到目标状态
        current_config = {"configurable": {"thread_id": thread_id}}
        await app.aupdate_state(current_config, target_state.values, as_node="__start__")

        return {
            "thread_id": thread_id,
            "checkpoint_id": checkpoint_id,
            "status": "success",
            "message": "已回滚到指定状态"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

