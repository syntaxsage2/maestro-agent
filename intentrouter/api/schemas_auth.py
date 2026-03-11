"""
认证相关的数据模型
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


# === 用户相关 ===

class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")


class UserCreate(UserBase):
    """用户注册请求"""
    password: str = Field(..., min_length=6, max_length=100, description="密码")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "zhangsan",
                "email": "zhangsan@example.com",
                "full_name": "张三",
                "password": "password123"
            }
        }


class UserUpdate(BaseModel):
    """用户更新请求"""
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像 URL")

    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "张三",
                "avatar_url": "https://example.com/avatar.jpg"
            }
        }


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "zhangsan",
                "email": "zhangsan@example.com",
                "full_name": "张三",
                "avatar_url": None,
                "is_active": True,
                "is_superuser": False,
                "created_at": "2025-10-28T10:00:00",
                "updated_at": "2025-10-28T10:00:00"
            }
        }


# === 认证相关 ===

class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "zhangsan",
                "password": "password123"
            }
        }


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str = Field(..., description="JWT 访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    user: UserResponse = Field(..., description="用户信息")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "username": "zhangsan",
                    "email": "zhangsan@example.com",
                    "full_name": "张三",
                    "avatar_url": None,
                    "is_active": True,
                    "is_superuser": False,
                    "created_at": "2025-10-28T10:00:00",
                    "updated_at": "2025-10-28T10:00:00"
                }
            }
        }


class TokenData(BaseModel):
    """Token 数据模型"""
    user_id: Optional[int] = None
    username: Optional[str] = None


# === 用户画像相关 ===

class UserProfileResponse(BaseModel):
    """用户画像响应"""
    user: UserResponse
    facts: list = Field(default_factory=list, description="用户事实")
    preferences: list = Field(default_factory=list, description="用户偏好")
    skills: list = Field(default_factory=list, description="用户技能")
    total_memories: int = Field(default=0, description="总记忆数")

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "id": 1,
                    "username": "zhangsan",
                    "email": "zhangsan@example.com",
                    "full_name": "张三",
                },
                "facts": [
                    {"content": "是一名 Python 开发者", "importance": 0.8}
                ],
                "preferences": [
                    {"content": "喜欢使用 LangChain", "importance": 0.7}
                ],
                "skills": [
                    {"content": "擅长 FastAPI 开发", "importance": 0.9}
                ],
                "total_memories": 3
            }
        }

