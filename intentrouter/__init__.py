"""
IntentRouter Pro - 意图驱动的多模态 Agent 编排系统
"""

__version__ = "0.1.0"

import os

from intentrouter.config import settings

# 设置 LangSmith 环境变量
os.environ["LANGCHAIN_TRACING_V2"] = settings.LANGCHAIN_TRACING_V2
os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT

print(f"✅ LangSmith 追踪已启用 - 项目: {settings.LANGCHAIN_PROJECT}")

