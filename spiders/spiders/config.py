"""
爬虫服务配置模块
使用 pydantic-settings 管理所有配置项，支持环境变量覆盖
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class SpiderConfig(BaseSettings):
    """爬虫全局配置"""

    # ==================== 数据库配置 ====================
    # 后端 API 地址（通过 API 写入数据，无需直连数据库）
    API_BASE_URL: str = "http://localhost:8000/api/v1"

    # Redis 连接地址（可选，用于去重）
    REDIS_URL: str = "redis://localhost:6379/0"

    # ==================== 请求配置 ====================
    # 请求最小延迟（秒）
    REQUEST_DELAY_MIN: float = 1.0

    # 请求最大延迟（秒）
    REQUEST_DELAY_MAX: float = 3.0

    # 请求超时时间（秒）
    REQUEST_TIMEOUT: int = 30

    # 最大重试次数
    MAX_RETRIES: int = 3

    # 重试间隔基础时间（秒），实际间隔 = base * 2^(retry_count)
    RETRY_BACKOFF_BASE: float = 2.0

    # ==================== 代理配置（可选） ====================
    # HTTP 代理地址，为空则不使用代理
    HTTP_PROXY: Optional[str] = None

    # HTTPS 代理地址，为空则不使用代理
    HTTPS_PROXY: Optional[str] = None

    # ==================== 各爬虫源开关 ====================
    # GitHub Trending 爬虫开关
    ENABLE_GITHUB_TRENDING: bool = True

    # Hacker News 爬虫开关
    ENABLE_HACKERNEWS: bool = True

    # Kaggle 比赛爬虫开关
    ENABLE_KAGGLE: bool = True

    # OpenAI 开发者计划爬虫开关
    ENABLE_OPENAI: bool = True

    # 天池比赛爬虫开关
    ENABLE_TIANCHI: bool = True

    # V2EX 爬虫开关
    ENABLE_V2EX: bool = True

    # 掘金 AI 标签爬虫开关
    ENABLE_JUEJIN: bool = True

    # ==================== 调度配置 ====================
    # 定时运行间隔（小时），0 表示不自动运行
    SCHEDULE_INTERVAL_HOURS: int = 6

    # 日志级别
    LOG_LEVEL: str = "INFO"

    # ==================== Playwright 配置 ====================
    # 是否使用无头模式
    HEADLESS: bool = True

    # 浏览器启动超时（毫秒）
    BROWSER_TIMEOUT: int = 30000

    model_config = {
        "env_prefix": "SPIDER_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# 全局配置单例
settings = SpiderConfig()
