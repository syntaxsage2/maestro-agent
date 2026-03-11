"""
配置管理模块

使用示例：
    from intentrouter.config import settings

    print(settings.openai_api_key)
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file="F:/Python/LangEnv.env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    # === LangSmith 配置 ===
    LANGCHAIN_TRACING_V2: str = "true"  # 启用追踪
    LANGCHAIN_ENDPOINT: str = ""
    LANGCHAIN_API_KEY: str = ""  # 你的 LangSmith API Key
    LANGCHAIN_PROJECT: str = ""  # 项目名称
    pythonunbuffered: str | None = None
    print(LANGCHAIN_TRACING_V2, LANGCHAIN_ENDPOINT, LANGCHAIN_API_KEY, LANGCHAIN_PROJECT)


    # LLM 配置
    openai_api_key: str = ""
    openai_base_url: str = ""
    model_name: str = "gpt-4o-mini"

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    # 工具配置
    WEATHER_API_KEY: str = ""  # OpenWeatherMap API Key（可选）
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    KNOWLEDGE_BASE_DIR: Path = BASE_DIR / "data" / "knowledge"

    # 数据库配置
    postgres_host: str = ""
    postgres_port: int = 5432
    postgres_db: str = ""
    postgres_user: str = ""
    postgres_password: str = ""

    # Redis 配置
    redis_url: str = "redis://localhost:6379/0"

    # 向量存储
    vector_store_type: str = "chroma"  # faiss | chroma | pgvector
    chroma_persist_directory: str = "data/chroma_db"  # 相对于项目根目录

    # 应用配置
    api_host: str = "localhost"
    api_port: int = 8000
    log_level: str = "INFO"
    
    # 可观测性
    langsmith_api_key: str = ""
    langsmith_project: str = "intentrouter-pro"
    
    @property
    def database_url(self) -> str:
        """构建数据库连接字符串"""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


# 全局配置实例
settings = Settings()

