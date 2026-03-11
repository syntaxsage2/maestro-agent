"""
用户管理模块
负责用户的 CRUD 操作
"""
from datetime import datetime
from typing import Optional, Dict, Any

from psycopg_pool import ConnectionPool
from pydantic import BaseModel

from intentrouter.utils.auth_utils import get_password_hash, verify_password


class User(BaseModel):
    """用户模型"""
    id: int
    username: str
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime


class UserManager:
    """用户管理器"""

    def __init__(self, pool: ConnectionPool):
        self.pool = pool

    def create_user(
            self,
            username: str,
            email: str,
            password: str,
            full_name: Optional[str] = None
    ) -> User:
        """
        创建新用户

        Args:
            username: 用户名
            email: 邮箱
            password: 明文密码
            full_name: 全名（可选）

        Returns:
            User: 创建的用户对象

        Raises:
            ValueError: 如果用户名或邮箱已存在
        """
        hashed_password = get_password_hash(password)
        print(hashed_password)

        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                # 检查用户名是否已存在
                cur.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cur.fetchone():
                    raise ValueError(f"用户名 '{username}' 已存在")

                # 检查邮箱是否已存在
                cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cur.fetchone():
                    raise ValueError(f"邮箱 '{email}' 已被注册")

                # 插入新用户
                cur.execute(
                    """
                    INSERT INTO users (username, email, hashed_password, full_name, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                    RETURNING id, username, email, hashed_password, full_name, avatar_url, 
                              is_active, is_superuser, created_at, updated_at
                    """,
                    (username, email, hashed_password, full_name)
                )
                row = cur.fetchone()
                conn.commit()

                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    hashed_password=row[3],
                    full_name=row[4],
                    avatar_url=row[5],
                    is_active=row[6],
                    is_superuser=row[7],
                    created_at=row[8],
                    updated_at=row[9]
                )

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户

        Args:
            username: 用户名

        Returns:
            Optional[User]: 用户对象，如果不存在则返回 None
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, username, email, hashed_password, full_name, avatar_url,
                           is_active, is_superuser, created_at, updated_at
                    FROM users
                    WHERE username = %s
                    """,
                    (username,)
                )
                row = cur.fetchone()

                if not row:
                    return None

                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    hashed_password=row[3],
                    full_name=row[4],
                    avatar_url=row[5],
                    is_active=row[6],
                    is_superuser=row[7],
                    created_at=row[8],
                    updated_at=row[9]
                )

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据 ID 获取用户

        Args:
            user_id: 用户 ID

        Returns:
            Optional[User]: 用户对象，如果不存在则返回 None
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, username, email, hashed_password, full_name, avatar_url,
                           is_active, is_superuser, created_at, updated_at
                    FROM users
                    WHERE id = %s
                    """,
                    (user_id,)
                )
                row = cur.fetchone()

                if not row:
                    return None

                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    hashed_password=row[3],
                    full_name=row[4],
                    avatar_url=row[5],
                    is_active=row[6],
                    is_superuser=row[7],
                    created_at=row[8],
                    updated_at=row[9]
                )

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        验证用户

        Args:
            username: 用户名
            password: 密码

        Returns:
            Optional[User]: 如果验证成功返回用户对象，否则返回 None
        """
        user = self.get_user_by_username(username)
        if not user:
            return None

        if not verify_password(password, user.hashed_password):
            return None

        if not user.is_active:
            return None

        return user

    def update_user(
            self,
            user_id: int,
            full_name: Optional[str] = None,
            avatar_url: Optional[str] = None
    ) -> Optional[User]:
        """
        更新用户信息

        Args:
            user_id: 用户 ID
            full_name: 全名（可选）
            avatar_url: 头像 URL（可选）

        Returns:
            Optional[User]: 更新后的用户对象
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                update_fields = []
                params = []

                if full_name is not None:
                    update_fields.append("full_name = %s")
                    params.append(full_name)

                if avatar_url is not None:
                    update_fields.append("avatar_url = %s")
                    params.append(avatar_url)

                if not update_fields:
                    return self.get_user_by_id(user_id)

                update_fields.append("updated_at = NOW()")
                params.append(user_id)

                query = f"""
                    UPDATE users
                    SET {', '.join(update_fields)}
                    WHERE id = %s
                    RETURNING id, username, email, hashed_password, full_name, avatar_url,
                              is_active, is_superuser, created_at, updated_at
                """

                cur.execute(query, params)
                row = cur.fetchone()
                conn.commit()

                if not row:
                    return None

                return User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    hashed_password=row[3],
                    full_name=row[4],
                    avatar_url=row[5],
                    is_active=row[6],
                    is_superuser=row[7],
                    created_at=row[8],
                    updated_at=row[9]
                )


# 全局实例
_user_manager: Optional[UserManager] = None


def get_user_manager() -> UserManager:
    """获取用户管理器单例"""
    global _user_manager
    if _user_manager is None:
        from intentrouter.db.checkpointer import _pool
        if _pool is None:
            # 使用同步连接池
            from psycopg_pool import ConnectionPool
            from intentrouter.config import settings

            sync_pool = ConnectionPool(
                conninfo=settings.database_url,
                max_size=20,
                kwargs={
                    "autocommit": True,
                    "prepare_threshold": 0
                }
            )
            _user_manager = UserManager(sync_pool)
        else:
            # 如果有异步连接池，需要创建同步版本
            from psycopg_pool import ConnectionPool
            from intentrouter.config import settings
            
            sync_pool = ConnectionPool(
                conninfo=settings.database_url,
                max_size=20,
                kwargs={
                    "autocommit": True,
                    "prepare_threshold": 0
                }
            )
            _user_manager = UserManager(sync_pool)
    
    return _user_manager

