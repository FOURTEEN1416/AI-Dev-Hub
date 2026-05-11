"""
基础爬虫模块
提供所有爬虫的公共功能：HTTP 请求、随机 User-Agent、频率控制、重试机制、
HTML 解析、Redis 去重、PostgreSQL 存储
"""

import asyncio
import logging
import random
import time
from abc import ABC, abstractmethod
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from spiders.config import settings
from spiders.models import OpportunityItem, SpiderResult

logger = logging.getLogger(__name__)


class BaseSpider(ABC):
    """
    基础爬虫抽象类
    所有具体爬虫必须继承此类并实现 parse() 方法
    """

    # 爬虫名称，子类必须覆盖
    name: str = "base"

    def __init__(self):
        """初始化基础爬虫"""
        self.ua = UserAgent()
        self._client: Optional[httpx.AsyncClient] = None
        self._redis = None
        self._db_engine = None
        self._db_session_factory = None

        # 运行统计
        self.items_count = 0
        self.filtered_count = 0
        self.duplicate_count = 0
        self.saved_count = 0
        self.error_count = 0
        self.start_time: Optional[float] = None

    # ==================== HTTP 客户端管理 ====================

    @property
    def client(self) -> httpx.AsyncClient:
        """获取或创建 HTTP 客户端（懒加载）"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.REQUEST_TIMEOUT),
                follow_redirects=True,
                headers=self._build_default_headers(),
            )
        return self._client

    def _build_default_headers(self) -> dict:
        """构建默认请求头，包含随机 User-Agent"""
        return {
            "User-Agent": self._get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    def _get_random_ua(self) -> str:
        """获取随机 User-Agent 字符串"""
        try:
            return self.ua.random
        except Exception:
            # 如果 fake_useragent 失败，使用备用 User-Agent 列表
            fallback_uas = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            ]
            return random.choice(fallback_uas)

    # ==================== 频率控制 ====================

    async def _random_delay(self) -> None:
        """随机延迟，避免请求过于频繁"""
        delay = random.uniform(settings.REQUEST_DELAY_MIN, settings.REQUEST_DELAY_MAX)
        logger.debug("[%s] 等待 %.2f 秒...", self.name, delay)
        await asyncio.sleep(delay)

    # ==================== 重试机制 ====================

    async def fetch(self, url: str, **kwargs) -> Optional[httpx.Response]:
        """
        带重试机制的 HTTP GET 请求

        Args:
            url: 请求地址
            **kwargs: 传递给 httpx 的额外参数

        Returns:
            httpx.Response 对象，请求全部失败时返回 None
        """
        max_retries = settings.MAX_RETRIES
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                # 每次请求前更新 User-Agent
                kwargs.setdefault("headers", {})
                kwargs["headers"]["User-Agent"] = self._get_random_ua()

                response = await self.client.get(url, **kwargs)
                response.raise_for_status()

                logger.debug(
                    "[%s] 请求成功: %s (状态码: %d, 第 %d 次尝试)",
                    self.name, url, response.status_code, attempt
                )
                return response

            except httpx.HTTPStatusError as e:
                last_error = e
                logger.warning(
                    "[%s] HTTP 错误: %s (状态码: %d, 第 %d/%d 次)",
                    self.name, url, e.response.status_code, attempt, max_retries
                )
                # 4xx 错误通常不需要重试
                if 400 <= e.response.status_code < 500:
                    return None

            except (httpx.RequestError, Exception) as e:
                last_error = e
                logger.warning(
                    "[%s] 请求异常: %s (%s, 第 %d/%d 次)",
                    self.name, url, str(e), attempt, max_retries
                )

            # 指数退避等待
            if attempt < max_retries:
                backoff = settings.RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
                wait_time = backoff + random.uniform(0, 1)
                logger.debug("[%s] 第 %d 次重试，等待 %.2f 秒...", self.name, attempt, wait_time)
                await asyncio.sleep(wait_time)

        logger.error("[%s] 请求最终失败: %s (错误: %s)", self.name, url, str(last_error))
        return None

    async def fetch_json(self, url: str, **kwargs) -> Optional[dict | list]:
        """
        带重试机制的 JSON API 请求

        Args:
            url: API 地址
            **kwargs: 传递给 httpx 的额外参数

        Returns:
            解析后的 JSON 数据，失败时返回 None
        """
        response = await self.fetch(url, **kwargs)
        if response is None:
            return None
        try:
            return response.json()
        except Exception as e:
            logger.error("[%s] JSON 解析失败: %s (%s)", self.name, url, str(e))
            return None

    # ==================== HTML 解析 ====================

    @staticmethod
    def parse_html(html_content: str, parser: str = "lxml") -> BeautifulSoup:
        """
        解析 HTML 内容为 BeautifulSoup 对象

        Args:
            html_content: HTML 字符串
            parser: 解析器，默认为 lxml

        Returns:
            BeautifulSoup 对象
        """
        return BeautifulSoup(html_content, parser)

    # ==================== Redis 去重 ====================

    async def _get_redis(self):
        """获取 Redis 连接（懒加载）"""
        if self._redis is None:
            import redis.asyncio as aioredis
            self._redis = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )
        return self._redis

    async def is_duplicate(self, source_url: str) -> bool:
        """
        基于 source_url 的 Redis SET 去重检查

        Args:
            source_url: 来源 URL

        Returns:
            True 表示已存在（重复），False 表示不存在
        """
        try:
            redis_client = await self._get_redis()
            redis_key = f"spider:dedup:{self.name}"
            is_dup = await redis_client.sismember(redis_key, source_url)
            if is_dup:
                logger.debug("[%s] 去重命中: %s", self.name, source_url)
                return True
            # 标记为已存在
            await redis_client.sadd(redis_key, source_url)
            return False
        except Exception as e:
            logger.warning("[%s] Redis 去重检查失败: %s", self.name, str(e))
            # Redis 不可用时跳过去重，允许数据通过
            return False

    async def close_redis(self) -> None:
        """关闭 Redis 连接"""
        if self._redis is not None:
            await self._redis.close()
            self._redis = None

    # ==================== PostgreSQL 存储 ====================

    async def _get_db_engine(self):
        """获取数据库引擎（懒加载）"""
        if self._db_engine is None:
            from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
            from sqlalchemy.orm import sessionmaker

            self._db_engine = create_async_engine(
                settings.DATABASE_URL,
                echo=False,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
            )
            self._db_session_factory = sessionmaker(
                self._db_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return self._db_engine, self._db_session_factory

    async def save_to_db(self, item: OpportunityItem) -> bool:
        """
        通过后端 API 保存单条数据

        Args:
            item: OpportunityItem 数据模型实例

        Returns:
            是否保存成功
        """
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                # 将 OpportunityItem 转换为 API 所需格式
                payload = {
                    "title": item.title,
                    "description": item.description,
                    "source_url": item.source_url,
                    "source": item.source,
                    "type": item.type,
                    "tags": item.tags or [],
                    "status": "active",
                }

                # 添加可选字段
                if getattr(item, 'reward', None):
                    payload["reward"] = item.reward
                if getattr(item, 'deadline', None):
                    payload["deadline"] = str(item.deadline)
                if getattr(item, 'requirements', None):
                    payload["requirements"] = item.requirements
                if getattr(item, 'official_link', None):
                    payload["official_link"] = item.official_link

                response = await client.post(
                    f"{settings.API_BASE_URL}/opportunities",
                    json=payload,
                )

                if response.status_code in (200, 201):
                    logger.debug("[%s] 数据入库成功: %s", self.name, item.title)
                    return True
                else:
                    logger.warning(
                        "[%s] 数据入库失败: %s (HTTP %s: %s)",
                        self.name, item.title, response.status_code, response.text[:200]
                    )
                    return False

        except Exception as e:
            logger.error("[%s] 数据入库失败: %s (%s)", self.name, item.title, str(e))
            return False

    async def save_batch_to_db(self, items: list[OpportunityItem]) -> int:
        """
        批量保存数据到 PostgreSQL

        Args:
            items: OpportunityItem 列表

        Returns:
            成功保存的条数
        """
        saved = 0
        for item in items:
            if await self.save_to_db(item):
                saved += 1
        return saved

    async def close_db(self) -> None:
        """关闭数据库连接"""
        if self._db_engine is not None:
            await self._db_engine.dispose()
            self._db_engine = None
            self._db_session_factory = None

    # ==================== 抽象方法 ====================

    @abstractmethod
    async def parse(self) -> list[OpportunityItem]:
        """
        解析方法，子类必须实现
        负责发起请求、解析数据、返回标准化后的 OpportunityItem 列表

        Returns:
            OpportunityItem 列表
        """
        ...

    # ==================== 运行入口 ====================

    async def run(self) -> SpiderResult:
        """
        运行爬虫的主入口方法
        包含完整的生命周期管理：初始化 -> 解析 -> 保存 -> 清理

        Returns:
            SpiderResult 运行结果统计
        """
        self.start_time = time.time()
        self.items_count = 0
        self.filtered_count = 0
        self.duplicate_count = 0
        self.saved_count = 0
        self.error_count = 0

        logger.info("=" * 60)
        logger.info("[%s] 爬虫开始运行", self.name)
        logger.info("=" * 60)

        try:
            # 执行解析
            items = await self.parse()
            self.items_count = len(items)

            # 去重检查
            unique_items = []
            for item in items:
                is_dup = await self.is_duplicate(item.source_url)
                if is_dup:
                    self.duplicate_count += 1
                else:
                    unique_items.append(item)

            # 批量入库
            self.saved_count = await self.save_batch_to_db(unique_items)

            logger.info(
                "[%s] 运行完成 - 采集: %d, 去重跳过: %d, 入库: %d",
                self.name, self.items_count, self.duplicate_count, self.saved_count
            )

        except Exception as e:
            logger.error("[%s] 运行异常: %s", self.name, str(e), exc_info=True)
            self.error_count += 1
            return SpiderResult(
                spider_name=self.name,
                items_count=self.items_count,
                filtered_count=self.filtered_count,
                duplicate_count=self.duplicate_count,
                saved_count=self.saved_count,
                error_count=self.error_count,
                duration=time.time() - self.start_time,
                success=False,
                error_message=str(e),
            )

        finally:
            # 清理资源
            await self.cleanup()

        duration = time.time() - self.start_time
        return SpiderResult(
            spider_name=self.name,
            items_count=self.items_count,
            filtered_count=self.filtered_count,
            duplicate_count=self.duplicate_count,
            saved_count=self.saved_count,
            error_count=self.error_count,
            duration=duration,
            success=True,
        )

    async def cleanup(self) -> None:
        """清理所有资源"""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
        await self.close_redis()
        await self.close_db()
        logger.debug("[%s] 资源清理完成", self.name)
