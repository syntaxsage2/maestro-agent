"""
长期记忆管理模块
Long-Term Memory(LTM) Manager
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from langchain_openai import OpenAIEmbeddings
from psycopg_pool import ConnectionPool
from pydantic import BaseModel

from intentrouter import settings


class Memory(BaseModel):
    """记忆模型"""
    id: Optional[int] = None
    user_id: str
    memory_type: str
    content: str
    importance: float = 0.5  # 0-1,重要程度
    created_at: Optional[datetime] = None
    accessed_at: Optional[datetime] = None
    access_count: int = 0

class LTMManager:
    """长期记忆管理器"""
    def __init__(self, pool: ConnectionPool):
        self.pool = pool
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_base_url
        )

    def add_memory(
            self,
            user_id: str,
            memory_type: str,
            content: str,
            importance: float = 0.5,
    ) -> int:
        """
        添加一条记忆

        Args:
            user_id: 用户ID
            memory_type: 记忆类型（fact/preference/skill）
            content: 记忆内容
            importance: 重要程度（0-1）

        Returns:
            记忆列表(按访问时间倒序)
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO long_term_memory 
                        (user_id, memory_type, content, importance, created_at, accessed_at)
                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                    RETURNING id
                    """,
                    (user_id, memory_type, content, importance)
                )
                memory_id = cur.fetchone()[0]
                conn.commit()
                return memory_id


    def get_user_memories(
            self,
            user_id: str,
            memory_type: Optional[str] = None,
            limit: int = 10,
    ) -> List[Memory]:
        """
        获取用户记忆列表

        Args:
            user_id: 用户ID
            memory_type: 可选，按类型筛选
            limit: 返回数量限制

        Returns:
            记忆列表（按访问时间倒序）
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                if memory_type:
                    cur.execute(
                        """
                        SELECT id, user_id, memory_type, content, importance, 
                               created_at, accessed_at, access_count
                        FROM long_term_memory
                        WHERE user_id = %s AND memory_type = %s
                        ORDER BY importance DESC, accessed_at DESC
                        LIMIT %s
                        """,
                        (user_id, memory_type, limit)
                    )
                else:
                    cur.execute(
                        """
                        SELECT id, user_id, memory_type, content, importance, 
                               created_at, accessed_at, access_count
                        FROM long_term_memory
                        WHERE user_id = %s
                        ORDER BY importance DESC, accessed_at DESC
                        LIMIT %s
                        """,
                        (user_id, limit)
                    )

                rows = cur.fetchall()
                memories = []
                for row in rows:
                    memories.append(Memory(
                        id=row[0],
                        user_id=str(row[1]),  # 转换为字符串
                        memory_type=row[2],
                        content=row[3],
                        importance=row[4],
                        created_at=row[5],
                        accessed_at=row[6],
                        access_count=row[7]
                    ))
                return memories


    def update_memory_access(self, memory_id: int):
        """更新记忆的访问信息(访问时间和访问次数)"""
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE long_term_memory
                    SET accessed_at = NOW(),
                        access_count = access_count + 1
                    WHERE id = %s
                    """, (memory_id,)
                )
                conn.commit()

    def delete_memory(self, memory_id: int):
        """删除一条记忆"""
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM long_term_memory WHERE id = %s",
                    (memory_id,)
                )
                conn.commit()

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户画像(汇总所有记忆)

        Returns:
            {
                "facts": [...],
                "preferences": [...],
                "skills": [...]
            }
        """
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT memory_type, content, importance
                    FROM long_term_memory
                    WHERE user_id = %s
                    ORDER BY importance DESC
                    """,
                    (user_id,)
                )
                rows = cur.fetchall()
                profile = {
                    "facts": [],
                    "preferences": [],
                    "skills": []
                }

                for row in rows:
                    memory_type, content, importance = row
                    if memory_type == "fact":
                        profile["facts"].append({"content": content, "importance": importance})
                    elif memory_type == "preference":
                        profile["preferences"].append({"content": content, "importance": importance})
                    elif memory_type == "skill":
                        profile["skills"].append({"content": content, "importance": importance})

            return profile


# 全局实例
_ltm_manager: Optional[LTMManager] = None


def get_ltm_manager() -> LTMManager:
    """获取LTM管理器单例"""
    global _ltm_manager
    if _ltm_manager is None:
        # 创建同步连接池（LTM Manager 需要同步池）
        from psycopg_pool import ConnectionPool
        from intentrouter.config import settings
        
        # 使用同步连接池
        sync_pool = ConnectionPool(
            conninfo=settings.database_url,
            max_size=20,
            kwargs={
                "autocommit": True,
                "prepare_threshold": 0
            }
        )
        
        # 初始化表结构（如果需要）
        try:
            sync_pool.connection()
        except Exception:
            pass
        
        _ltm_manager = LTMManager(sync_pool)
    return _ltm_manager