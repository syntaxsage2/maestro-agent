"""
API 数据模型
"""
from typing import Optional, List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户信息", min_length=1)
    thread_id: Optional[str] = Field(None, description="会话ID(可选, 不提供则创建新会话)")
    user_id: Optional[str] = Field(None, description="用户ID")
    stream: bool = Field(False, description="是否流式返回")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Python 的 asyncio 怎么用?",
                "thread_id": "abc-123",
                "stream": False,
            }
        }


# === 多模态 Schemas ===

class ImageAttachment(BaseModel):
    """图片附件"""
    url: Optional[str] = Field(None, description="图片 URL（http/https）")
    data: Optional[str] = Field(None, description="图片 base64 数据（data URI）")
    name: Optional[str] = Field("image", description="文件名")
    mime_type: Optional[str] = Field("image/jpeg", description="MIME 类型")

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://example.com/image.jpg",
                "name": "screenshot.jpg",
                "mime_type": "image/jpeg"
            }
        }


class MultimodalChatRequest(BaseModel):
    """多模态聊天请求（支持图片）"""
    message: str = Field(..., description="用户信息")
    attachments: List[ImageAttachment] = Field(default_factory=list, description="图片附件列表")
    thread_id: Optional[str] = Field(None, description="会话ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    stream: bool = Field(False, description="是否流式返回")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "这张图片里有什么？",
                "attachments": [
                    {
                        "url": "https://example.com/image.jpg",
                        "name": "photo.jpg"
                    }
                ],
                "thread_id": "abc-123"
            }
        }


class MultimodalAnalysis(BaseModel):
    """多模态分析结果"""
    type: str = Field(..., description="分析类型")
    images_count: int = Field(..., description="图片数量")
    result: str = Field(..., description="分析结果")


class MultimodalChatResponse(BaseModel):
    """多模态聊天响应"""
    thread_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="助手回复")
    intent: Optional[str] = Field(None, description="识别意图")
    route: Optional[str] = Field(None, description="路由决策")
    multimodal_analysis: Optional[MultimodalAnalysis] = Field(None, description="多模态分析结果")

    class Config:
        json_schema_extra = {
            "example": {
                "thread_id": "abc-123",
                "message": "这张图片显示了...",
                "intent": "multimodal",
                "route": "vision_agent",
                "multimodal_analysis": {
                    "type": "vqa",
                    "images_count": 1,
                    "result": "图片中包含..."
                }
            }
        }


class Message(BaseModel):
    """消息"""
    role: str = Field(..., description="角色:human 或 ai")
    content: str = Field(..., description="消息内容")


class ChatResponse(BaseModel):
    """聊天响应"""
    thread_id: str = Field(..., description="会话ID")
    message: str = Field(..., description="助手回复")
    intent: Optional[str] = Field(None, description="识别意图")
    route: Optional[str] = Field(None, description="路由决策")
    retrieved_docs_count: int = Field(0, description="检索文档数量")

    class Config:
        json_schema_extra = {
            "example": {
                "thread_id": "abc-123",
                "message": "AsyncIO 是 Python 的异步 I/O 库...",
                "intent": "simple_qa",
                "route": "rag_agent",
                "retrieved_docs_count": 4,
            }
        }


class HistoryResponse(BaseModel):
    """历史记录响应"""
    thread_id: str
    messages: List[Message]
    intent: Optional[str] = None
    route: Optional[str] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    error: str
    detail: Optional[str] = None