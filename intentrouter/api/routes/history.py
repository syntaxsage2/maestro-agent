"""
历史记录相关路由
"""
from fastapi import APIRouter, HTTPException, Depends

from intentrouter.api.schemas import HistoryResponse, Message
from intentrouter.graph.main_graph import create_graph
from intentrouter.api.routes.auth import get_current_user
from intentrouter.db.user_manager import User

router = APIRouter()

# 复用 graph 实例
_graph = None

async def get_graph():
    global _graph
    if _graph is None:
        _graph = await create_graph()
    return _graph

@router.get("/history/{thread_id}", response_model=HistoryResponse)
async def get_history(
        thread_id: str,
        current_user: User = Depends(get_current_user)
):
    """
    获取会话历史
    
    需要登录才能使用，只能查看自己的会话历史

    Args:
        thread_id: 用户级别的会话ID
        current_user: 当前登录用户

    Returns:
        HistoryResponse: 历史记录
    """
    try:
        app = await get_graph()
        
        # 使用复合key: user_id + thread_id
        user_id = str(current_user.id)
        composite_thread_id = f"{user_id}_{thread_id}"
        config = {"configurable": {"thread_id": composite_thread_id}}

        # 获取状态 - 使用 graph 的 get_state 方法
        state = await app.aget_state(config)

        if not state.values:
            raise HTTPException(status_code=404, detail="会话不存在")

        # 转换消息格式
        messages = [
            Message(
                role=msg.type,
                content=msg.content
            ) for msg in state.values.get("messages", [])
        ]

        return HistoryResponse(
            thread_id=thread_id,
            messages=messages,
            intent=state.values.get("intent"),
            route=state.values.get("route_decision"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{thread_id}/tools")
async def get_tool_history(
        thread_id: str,
        current_user: User = Depends(get_current_user)
):
    """
    获取会话的工具调用历史
    
    需要登录才能使用，只能查看自己的工具调用历史
    
    Args:
        thread_id: 用户级别的会话ID
        current_user: 当前登录用户
        
    Returns:
        工具调用历史列表
    """
    try:
        # 使用复合key: user_id + thread_id
        user_id = str(current_user.id)
        composite_thread_id = f"{user_id}_{thread_id}"
        config = {"configurable": {"thread_id": composite_thread_id}}
        
        # 获取状态 - 使用 graph
        app = await get_graph()
        state = await app.aget_state(config)
        
        if not state.values:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 提取工具调用信息
        tools_used = state.values.get("tools_used", [])
        tool_results = state.values.get("tool_results", {})
        
        # 从消息中提取工具调用详情
        tool_calls = []
        messages = state.values.get("messages", [])
        
        for i, msg in enumerate(messages):
            # AIMessage with tool_calls
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                for tc in msg.tool_calls:
                    # 找到对应的 ToolMessage
                    result = None
                    if i + 1 < len(messages):
                        next_msg = messages[i + 1]
                        if hasattr(next_msg, 'content'):
                            result = next_msg.content
                    
                    tool_calls.append({
                        "name": tc["name"],
                        "args": tc["args"],
                        "result": result,
                        "timestamp": i  # 使用消息索引作为时间戳
                    })
        
        return {
            "thread_id": thread_id,
            "tools_used": tools_used,
            "tool_calls": tool_calls,
            "total_calls": len(tool_calls)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{thread_id}")
async def delete_history(
        thread_id: str,
        current_user: User = Depends(get_current_user)
):
    """
    删除会话历史
    
    需要登录才能使用，只能删除自己的会话历史
    
    Args:
        thread_id: 用户级别的会话ID
        current_user: 当前登录用户
        
    Returns:
        删除结果
    """
    try:
        # 使用复合key: user_id + thread_id
        user_id = str(current_user.id)
        composite_thread_id = f"{user_id}_{thread_id}"
        config = {"configurable": {"thread_id": composite_thread_id}}
        
        app = await get_graph()
        
        # 检查是否存在
        state = await app.aget_state(config)
        if not state.values:
            raise HTTPException(status_code=404, detail="会话不存在")
        
        # 清空状态
        await app.aupdate_state(config, {"messages": []}, as_node="__start__")
        
        return {
            "thread_id": thread_id,
            "status": "deleted",
            "message": "会话历史已删除"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
