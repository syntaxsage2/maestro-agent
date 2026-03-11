"""
认证相关路由
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from intentrouter.api.schemas_auth import (
    UserCreate,
    UserResponse,
    LoginRequest,
    LoginResponse,
    UserUpdate,
    UserProfileResponse
)
from intentrouter.db.user_manager import get_user_manager, User
from intentrouter.db.ltm_manager import get_ltm_manager
from intentrouter.utils.auth_utils import create_access_token, decode_access_token

router = APIRouter()
security = HTTPBearer()


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    从 JWT token 获取当前用户

    Args:
        credentials: HTTP Bearer 认证凭据

    Returns:
        User: 当前用户

    Raises:
        HTTPException: 如果 token 无效或用户不存在
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_manager = get_user_manager()
    user = user_manager.get_user_by_id(int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    return user


def get_current_user_optional(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    可选的用户认证（不强制要求登录）

    Args:
        credentials: HTTP Bearer 认证凭据（可选）

    Returns:
        Optional[User]: 当前用户，如果未登录则返回 None
    """
    if credentials is None:
        return None

    try:
        return get_current_user(credentials)
    except HTTPException:
        return None


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate):
    """
    用户注册

    Args:
        user_create: 用户注册信息

    Returns:
        LoginResponse: 包含 token 和用户信息的响应
    """
    user_manager = get_user_manager()

    try:
        # 创建用户
        user = user_manager.create_user(
            username=user_create.username,
            email=user_create.email,
            password=user_create.password,
            full_name=user_create.full_name
        )

        # 生成 access token
        access_token = create_access_token(data={"sub": str(user.id)})

        # 返回响应
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                full_name=user.full_name,
                avatar_url=user.avatar_url,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    """
    用户登录

    Args:
        login_request: 登录请求

    Returns:
        LoginResponse: 包含 token 和用户信息的响应
    """
    user_manager = get_user_manager()

    # 验证用户
    user = user_manager.authenticate_user(
        username=login_request.username,
        password=login_request.password
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 生成 access token
    access_token = create_access_token(data={"sub": str(user.id)})

    # 返回响应
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    获取当前用户信息

    Args:
        current_user: 当前登录用户

    Returns:
        UserResponse: 用户信息
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar_url=current_user.avatar_url,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
        user_update: UserUpdate,
        current_user: User = Depends(get_current_user)
):
    """
    更新当前用户信息

    Args:
        user_update: 用户更新信息
        current_user: 当前登录用户

    Returns:
        UserResponse: 更新后的用户信息
    """
    user_manager = get_user_manager()

    updated_user = user_manager.update_user(
        user_id=current_user.id,
        full_name=user_update.full_name,
        avatar_url=user_update.avatar_url
    )

    if updated_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    return UserResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        full_name=updated_user.full_name,
        avatar_url=updated_user.avatar_url,
        is_active=updated_user.is_active,
        is_superuser=updated_user.is_superuser,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at
    )


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """
    获取用户画像（包含用户信息和长期记忆）

    Args:
        current_user: 当前登录用户

    Returns:
        UserProfileResponse: 用户画像
    """
    ltm_manager = get_ltm_manager()

    # 获取用户的长期记忆画像
    profile = ltm_manager.get_user_profile(str(current_user.id))

    return UserProfileResponse(
        user=UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            full_name=current_user.full_name,
            avatar_url=current_user.avatar_url,
            is_active=current_user.is_active,
            is_superuser=current_user.is_superuser,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        ),
        facts=profile.get("facts", []),
        preferences=profile.get("preferences", []),
        skills=profile.get("skills", []),
        total_memories=len(profile.get("facts", [])) + len(profile.get("preferences", [])) + len(
            profile.get("skills", []))
    )

