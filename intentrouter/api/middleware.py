"""
API 中间件
"""
import time
import uuid
import logging
from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from langgraph.errors import GraphInterrupt

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("intentrouter.api")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求 ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 记录请求开始
        start_time = time.time()
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - 开始"
        )

        # 处理请求
        try:
            response = await call_next(request)

            # 记录请求完成
            duration = time.time() - start_time
            logger.info(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"完成 {response.status_code} ({duration:.2f}s)"
            )

            # 添加请求 ID 到响应头
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"[{request_id}] {request.method} {request.url.path} - "
                f"错误 ({duration:.2f}s): {str(e)}",
                exc_info=True
            )
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """全局错误处理中间件"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)

        except GraphInterrupt as e:
            # LangGraph 中断异常 - 这是正常的 HITL 流程
            request_id = getattr(request.state, "request_id", "unknown")
            logger.info(f"[{request_id}] GraphInterrupt: {e}")

            # 提取中断信息
            interrupt_info = {}
            if hasattr(e, 'interrupts') and e.interrupts:
                interrupt_info = e.interrupts[0].value if e.interrupts else {}

            return JSONResponse(
                status_code=status.HTTP_202_ACCEPTED,
                content={
                    "status": "interrupted",
                    "message": "操作需要人工确认",
                    "interrupt_info": interrupt_info,
                    "request_id": request_id
                }
            )

        except ValueError as e:
            # 参数错误
            request_id = getattr(request.state, "request_id", "unknown")
            logger.warning(f"[{request_id}] ValueError: {str(e)}")

            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "error": "参数错误",
                    "detail": str(e),
                    "request_id": request_id
                }
            )

        except Exception as e:
            # 其他未捕获的异常
            request_id = getattr(request.state, "request_id", "unknown")
            logger.error(
                f"[{request_id}] Unhandled exception: {str(e)}",
                exc_info=True
            )

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "服务器内部错误",
                    "detail": str(e),
                    "request_id": request_id
                }
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """简单的速率限制中间件（基于内存）"""

    def __init__(self, app, max_requests: int = 100, window: int = 60):
        """
        Args:
            app: FastAPI 应用
            max_requests: 时间窗口内最大请求数
            window: 时间窗口（秒）
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = {}  # {ip: [(timestamp, count), ...]}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 获取客户端 IP
        client_ip = request.client.host if request.client else "unknown"

        # 清理过期记录
        current_time = time.time()
        if client_ip in self.requests:
            self.requests[client_ip] = [
                (ts, count) for ts, count in self.requests[client_ip]
                if current_time - ts < self.window
            ]

        # 检查速率限制
        if client_ip in self.requests:
            total_requests = sum(count for _, count in self.requests[client_ip])

            if total_requests >= self.max_requests:
                logger.warning(f"Rate limit exceeded for {client_ip}")
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "请求过于频繁",
                        "detail": f"每 {self.window} 秒最多 {self.max_requests} 个请求"
                    }
                )

        # 记录请求
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        self.requests[client_ip].append((current_time, 1))

        # 继续处理
        response = await call_next(request)

        # 添加速率限制信息到响应头
        remaining = self.max_requests - sum(
            count for _, count in self.requests.get(client_ip, [])
        )
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window))
        
        return response

