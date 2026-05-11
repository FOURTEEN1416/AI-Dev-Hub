"""
应用配置管理模块
使用 pydantic-settings 管理所有应用配置，支持环境变量覆盖
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类，从环境变量或 .env 文件加载配置"""

    # 数据库配置（默认使用 SQLite 进行本地测试）
    DATABASE_URL: str = "sqlite+aiosqlite:///./ai_dev_hub.db"
    SYNC_DATABASE_URL: str = "sqlite:///./ai_dev_hub.db"

    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT 认证配置
    SECRET_KEY: str = "ai-dev-hub-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24小时

    # 邮件配置
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "noreply@ai-dev-hub.com"
    FRONTEND_URL: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# 全局配置实例
settings = Settings()
