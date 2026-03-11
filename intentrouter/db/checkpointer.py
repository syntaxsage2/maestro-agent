"""
Checkpointer 管理模块

提供同步版本的 Checkpointer，兼容同步和异步调用
"""
import asyncio

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from psycopg_pool.pool_async import AsyncConnectionPool

from intentrouter.config import settings

# 全局实例（延迟初始化）
_checkpointer: PostgresSaver | None = None
_async_checkpointer: AsyncPostgresSaver | None = None
_setup_done = False
_pool: ConnectionPool | None = None
_async_pool: AsyncConnectionPool | None = None


def _init_checkpointer():
    """内部：初始化同步 Checkpointer"""
    global _checkpointer, _pool, _setup_done
    
    if _checkpointer is None:
        # 创建同步连接池
        _pool = ConnectionPool(
            conninfo=settings.database_url,
            max_size=20,
            kwargs={
                "autocommit": True,
                "row_factory": dict_row,
            }
        )
        
        # 创建 PostgresSaver（同步版本）
        _checkpointer = PostgresSaver.from_conn(_pool)
        
        # 初始化表结构
        if not _setup_done:
            _checkpointer.setup()
            _setup_done = True
            print("✅ PostgresSaver (sync) 初始化完成")

async def _init_async_checkpointer():
    """内部：初始化异步 Checkpointer"""
    global _async_checkpointer, _async_pool, _setup_done
    
    if _async_checkpointer is None:
        # 创建异步连接池
        _async_pool = AsyncConnectionPool(
            conninfo=settings.database_url,
            max_size=20,
            kwargs={
                "autocommit": True,
                "row_factory": dict_row,
            }
        )
        
        # 创建 AsyncPostgresSaver
        _async_checkpointer = AsyncPostgresSaver(_async_pool)
        
        # 初始化表结构
        if not _setup_done:
            await _async_checkpointer.setup()
            _setup_done = True
            print("✅ AsyncPostgresSaver (async) 初始化完成")


def get_checkpointer() -> PostgresSaver:
    """获取同步 Checkpointer 实例"""
    global _checkpointer
    if _checkpointer is None:
        _init_checkpointer()
    return _checkpointer


async def get_async_checkpointer() -> AsyncPostgresSaver:
    """获取异步 Checkpointer 实例"""
    global _async_checkpointer
    if _async_checkpointer is None:
        await _init_async_checkpointer()
    return _async_checkpointer


def close_checkpointer():
    """关闭所有 Checkpointer 和连接池"""
    global _pool, _async_pool
    if _pool:
        _pool.close()
        print("🔌 Sync Checkpointer 连接池已关闭")
    
    # 异步池的关闭需要在事件循环中运行
    if _async_pool:
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                loop.create_task(_async_pool.close())
            else:
                asyncio.run(_async_pool.close())
            print("🔌 Async Checkpointer 连接池已关闭")
        except RuntimeError: # No running loop
            asyncio.run(_async_pool.close())
            print("🔌 Async Checkpointer 连接池已关闭")
