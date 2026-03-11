import json
import uuid
from typing import Optional, AsyncGenerator, List

from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Depends
from langchain_core.messages import HumanMessage
from langchain_core.runnables.graph import Graph
from fastapi.responses import StreamingResponse
from intentrouter.api.schemas import ChatResponse, ChatRequest, MultimodalChatResponse, MultimodalChatRequest
from intentrouter.graph.main_graph import create_graph
from intentrouter.utils.image_utils import encode_image_bytes_to_base64, resize_image_if_needed

# 导入认证依赖
from intentrouter.api.routes.auth import get_current_user, get_current_user_optional
from intentrouter.db.user_manager import User

router = APIRouter()

_graph = None


async def get_graph():
    global _graph
    if _graph is None:
        _graph = await create_graph()
    return _graph


@router.post("/chat", response_model=ChatResponse)
async def chat(
        request: ChatRequest,
        current_user: User = Depends(get_current_user)
):
    """
    对话接口(非流式)
    
    需要登录才能使用

    Args:
        request: 聊天请求
        current_user: 当前登录用户

    Returns:
        ChatResponse: 聊天响应
    """
    try:
        app = await get_graph()

        # 使用当前用户的 ID
        user_id = str(current_user.id)
        
        # 生成或使用thread_id (用户级别的thread_id)
        user_thread_id = request.thread_id or str(uuid.uuid4())
        
        # 使用复合key: user_id + thread_id 来隔离不同用户的会话
        composite_thread_id = f"{user_id}_{user_thread_id}"
        config = {"configurable": {"thread_id": composite_thread_id}}

        # 调用graph
        result = app.invoke({
            "messages": [HumanMessage(content=request.message)],
            "user_id": user_id
        }, config=config)

        # 提取回复
        assistant_message = result["messages"][-1].content

        return ChatResponse(
            thread_id=user_thread_id,  # 返回用户级别的thread_id，不暴露复合key
            message = assistant_message,
            intent=result.get("intent"),
            route=result.get("route"),
            retrieved_docs_count=len(result.get("retrieved_docs", []))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def stream_chat_response(
        message: str,
        thread_id: str,
        user_id: str
) -> AsyncGenerator[str, None]:
    """
    流式响应生成器（真·流式版）
    
    Args:
        message: 用户消息
        thread_id: 会话 ID
        user_id: 用户 ID

    Yields:
        str: SSE 格式的数据流
        
    事件格式：
    - start: 开始
    - node_start: 节点开始执行
    - node_end: 节点执行完成
    - token: AI回复的增量内容（单个token）
    - chunk: AI回复的增量内容块
    - message: 完整消息
    - metadata: 本轮对话的元数据 (intent, route等)
    - done: 完成
    """
    try:
        app = await get_graph()
        config = {"configurable": {"thread_id": thread_id}}
        
        # 定义输入
        inputs = {
            "messages": [HumanMessage(content=message)],
            "user_id": user_id
        }
        
        print(f"🚀 [SSE] 开始流式响应: thread_id={thread_id[:8]}..., message={message[:50]}")

        # 1. 发送开始事件
        start_data = f"data: {json.dumps({'event': 'start'}, ensure_ascii=False)}\n\n"
        yield start_data
        print(f"✉️  [SSE] Sent start event")
        
        # 2. 使用 astream_events 实时获取事件
        final_content = ""
        current_node = None
        event_count = 0
        ai_response = None  # 保存AI的回复
        final_intent = None
        
        print(f"📡 [SSE] 开始监听 astream_events...")
        async for event in app.astream_events(inputs, config=config, version="v1"):
            event_count += 1
            kind = event["event"]
            name = event.get("name", "")
            
            # 调试：打印所有on_chain_end事件
            if kind == "on_chain_end":
                print(f"🔍 [DEBUG] on_chain_end: name={name}")
            
            # 节点开始执行
            if kind == "on_chain_start" and name in ["entry", "router", "rag_agent", "tool_call", "tool_execute", "planner", "executor", "vision_agent", "writer_agent", "output", "memory_extractor"]:
                if current_node != name:
                    current_node = name
                    node_data = {
                        'event': 'node_start',
                        'node': name
                    }
                    data_str = f"data: {json.dumps(node_data, ensure_ascii=False)}\n\n"
                    yield data_str
                    print(f"✉️  [SSE] Sent node_start: {name}")
            
            # 节点执行完成
            elif kind == "on_chain_end" and current_node and name == current_node:
                # 如果是output节点结束，获取AI的回复
                if name == "output":
                    output_data = event["data"].get("output")
                    if output_data and output_data.get("messages"):
                        ai_response = output_data["messages"][-1].content
                        print(f"💬 [DEBUG] 捕获到output节点的AI回复: {ai_response[:100]}...")
                
                # 如果是router节点结束，获取intent
                if name == "router":
                    router_data = event["data"].get("output")
                    if router_data:
                        final_intent = router_data.get("intent")
                        print(f"🎯 [DEBUG] 捕获到intent: {final_intent}")
                
                node_data = {
                    'event': 'node_end',
                    'node': current_node
                }
                data_str = f"data: {json.dumps(node_data, ensure_ascii=False)}\n\n"
                yield data_str
                print(f"✉️  [SSE] Sent node_end: {current_node}")
                current_node = None
            
            # LLM 流式输出 (token级别)
            elif kind == "on_chat_model_stream":
                chunk = event["data"]["chunk"]
                if hasattr(chunk, 'content') and chunk.content:
                    content_piece = chunk.content
                    final_content += content_piece
                    # 发送 token 事件
                    token_data = {
                        'event': 'token',
                        'content': content_piece
                    }
                    data_str = f"data: {json.dumps(token_data, ensure_ascii=False)}\n\n"
                    yield data_str
                    print(f"✉️  [SSE] Sent token: {content_piece[:20] if len(content_piece) > 20 else content_piece}...")

            # 主图执行完成，发送最终消息
            elif kind == "on_chain_end" and name == "LangGraph":
                # 如果没有从 output 节点拿到，从最终状态对象兜底提取
                if not ai_response:
                    final_state = event["data"].get("output", {})
                    if final_state and isinstance(final_state, dict):
                        from langchain_core.messages import AIMessage
                        messages = final_state.get("messages", [])
                        for msg in reversed(messages):
                            if isinstance(msg, AIMessage) and msg.content:
                                ai_response = msg.content
                                break

                # 如果捕获到了AI回复，发送message事件
                if ai_response:
                    message_data = {
                        'event': 'message',
                        'node': 'output',
                        'role': 'ai',
                        'content': ai_response
                    }
                    data_str = f"data: {json.dumps(message_data, ensure_ascii=False)}\n\n"
                    yield data_str
                    print(f"✉️  [SSE] Sent message: {ai_response[:50]}...")
                else:
                    print(f"⚠️  [WARN] LangGraph结束但没有AI回复")
                
                # 发送元数据
                metadata = {
                    'event': 'metadata',
                    'intent': final_intent,
                    'route': None,
                    'retrieved_docs_count': 0
                }
                data_str = f"data: {json.dumps(metadata, ensure_ascii=False)}\n\n"
                yield data_str
                print(f"✉️  [SSE] Sent metadata: intent={final_intent}")

        # 3. 结束标记
        done_data = f"data: {json.dumps({'event': 'done'}, ensure_ascii=False)}\n\n"
        yield done_data
        print(f"✉️  [SSE] Sent done event")
        print(f"✅ [SSE] 流正常完成: thread_id={thread_id[:8]}..., 共处理 {event_count} 个事件")

    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        print(f"❌ SSE流式响应错误: {error_detail}")

        error_data = {
            "event": "error",
            "data": {
                "error": f"An error occurred: {str(e)}",
                "type": type(e).__name__
            }
        }
        try:
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
        except Exception as yield_e:
            print(f"❌ 无法向客户端发送错误信息: {yield_e}")
        
        print(f"❌ 因异常终止SSE流: thread_id={thread_id[:8]}...")


@router.post("/chat/stream")
async def chat_stream(
        request: ChatRequest,
        current_user: User = Depends(get_current_user)
):
    """
    流式对话接口
    
    需要登录才能使用
    支持实时推送节点执行进度和消息生成

    Args:
        request: 聊天请求
        current_user: 当前登录用户

    Returns:
        StreamingResponse: SSE 流式响应
        
    使用示例：
    ```javascript
    const eventSource = new EventSource('/api/chat/stream');
    eventSource.onmessage = (e) => {
        const data = JSON.parse(e.data);
        console.log(data.event, data);
    };
    ```
    """
    user_id = str(current_user.id)
    user_thread_id = request.thread_id or str(uuid.uuid4())
    
    # 使用复合key: user_id + thread_id
    composite_thread_id = f"{user_id}_{user_thread_id}"

    return StreamingResponse(
        stream_chat_response(request.message, composite_thread_id, user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 Nginx 缓冲
            "X-Thread-ID": user_thread_id  # 返回用户级别的thread_id
        }
    )


@router.post("/chat/multimodal", response_model=MultimodalChatResponse)
async def chat_multimodal(
        message: str = Form(..., description="用户消息"),
        files: List[UploadFile] = File(default=[], description="上传的图片文件"),
        thread_id: Optional[str] = Form(None, description="会话ID"),
        current_user: User = Depends(get_current_user)
):
    """
    多模态聊天接口（支持图片上传）
    
    需要登录才能使用

    使用方式：
    ```bash
    curl -X POST http://localhost:8000/chat/multimodal \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -F "message=这张图片里有什么？" \
      -F "files=@image1.jpg" \
      -F "files=@image2.jpg"
    ```
    """
    try:
        user_id = str(current_user.id)
        user_thread_id = thread_id or str(uuid.uuid4())
        
        # 使用复合key: user_id + thread_id
        composite_thread_id = f"{user_id}_{user_thread_id}"
        
        # 1. 处理上传的图片
        attachments = []

        for file in files:
            # 读取文件
            image_bytes = await file.read()

            # 调整大小（如果过大）
            image_bytes = resize_image_if_needed(image_bytes, max_size=2000)

            # 编码为 base64
            mime_type = file.content_type or "image/jpeg"
            base64_data = encode_image_bytes_to_base64(image_bytes, mime_type)

            attachments.append({
                "data": base64_data,
                "url": base64_data,  # 兼容性
                "name": file.filename,
                "mime_type": mime_type
            })

        print(f"📸 收到 {len(attachments)} 张图片")

        # 2. 构建消息
        from langchain_core.messages import HumanMessage

        # 3. 调用 Graph
        graph = await create_graph()
        
        config = {"configurable": {"thread_id": composite_thread_id}}

        result = await graph.ainvoke({
            "messages": [HumanMessage(content=message)],
            "attachments": attachments,
            "user_id": user_id
        }, config=config)

        # 4. 返回结果
        return MultimodalChatResponse(
            thread_id=user_thread_id,  # 返回用户级别的thread_id
            message=result["messages"][-1].content,
            intent=result.get("intent"),
            route=result.get("route_decision"),
            multimodal_analysis=result.get("multimodal_analysis")
        )

    except Exception as e:
        print(f"❌ 多模态聊天错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat/multimodal/json", response_model=MultimodalChatResponse)
async def chat_multimodal_json(
        request: MultimodalChatRequest,
        current_user: User = Depends(get_current_user)
):
    """
    多模态聊天接口（JSON 格式，支持 URL 或 base64）
    
    需要登录才能使用

    使用方式：
    ```bash
    curl -X POST http://localhost:8000/chat/multimodal/json \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -d '{
        "message": "分析这张图片",
        "attachments": [
          {"url": "https://example.com/image.jpg"}
        ]
      }'
    ```
    """
    try:
        user_id = str(current_user.id)
        user_thread_id = request.thread_id or str(uuid.uuid4())
        
        # 使用复合key: user_id + thread_id
        composite_thread_id = f"{user_id}_{user_thread_id}"
        
        # 转换 attachments
        attachments = []
        for att in request.attachments:
            attachments.append({
                "url": att.url or att.data,
                "data": att.data,
                "name": att.name,
                "mime_type": att.mime_type
            })

        # 调用 Graph
        from langchain_core.messages import HumanMessage
        graph = await create_graph()
        
        config = {"configurable": {"thread_id": composite_thread_id}}

        result = await graph.ainvoke({
            "messages": [HumanMessage(content=request.message)],
            "attachments": attachments,
            "user_id": user_id
        }, config=config)

        return MultimodalChatResponse(
            thread_id=user_thread_id,  # 返回用户级别的thread_id
            message=result["messages"][-1].content,
            intent=result.get("intent"),
            route=result.get("route_decision"),
            multimodal_analysis=result.get("multimodal_analysis")
        )

    except Exception as e:
        print(f"❌ 多模态聊天错误: {e}")
        raise HTTPException(status_code=500, detail=str(e))