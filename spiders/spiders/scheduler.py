"""
爬虫调度器模块
使用 asyncio 管理所有爬虫，支持手动触发和定时运行
"""

import asyncio
import logging
from typing import Optional
from datetime import datetime

from spiders.config import settings
from spiders.models import SpiderResult
from spiders.base import BaseSpider

logger = logging.getLogger(__name__)


class SpiderScheduler:
    """
    爬虫调度器
    管理所有爬虫的注册、触发和定时运行
    """

    def __init__(self):
        """初始化调度器"""
        self._spiders: dict[str, BaseSpider] = {}
        self._running = False
        self._scheduled_task: Optional[asyncio.Task] = None
        self._engine_label = self._detect_engine()

    @staticmethod
    def _detect_engine() -> str:
        """检测当前启用的引擎组合，返回标识符"""
        engine = "httpx+BS4"
        try:
            from spiders.base import _SCRAPLING_AVAILABLE
            if _SCRAPLING_AVAILABLE and settings.ENABLE_SCRAPLING:
                engine = "Scrapling(AsyncFetcher+StealthyFetcher)"
        except Exception:
            pass
        ai_ext = "AI提取" if settings.ENABLE_AI_EXTRACT else "无AI提取"
        stealth = "Stealthy" if settings.SCRAPLING_SOLVE_CLOUDFLARE else "普通模式"
        return f"{engine} / {ai_ext} / Cloudflare:{stealth}"

    # ==================== 爬虫注册 ====================

    def register(self, spider: BaseSpider) -> None:
        """
        注册爬虫到调度器

        Args:
            spider: 爬虫实例
        """
        self._spiders[spider.name] = spider
        logger.info("注册爬虫: %s", spider.name)

    def unregister(self, spider_name: str) -> None:
        """
        从调度器移除爬虫

        Args:
            spider_name: 爬虫名称
        """
        if spider_name in self._spiders:
            del self._spiders[spider_name]
            logger.info("移除爬虫: %s", spider_name)

    def get_spider(self, spider_name: str) -> Optional[BaseSpider]:
        """
        获取指定爬虫实例

        Args:
            spider_name: 爬虫名称

        Returns:
            爬虫实例，未找到返回 None
        """
        return self._spiders.get(spider_name)

    def list_spiders(self) -> list[str]:
        """
        列出所有已注册的爬虫名称

        Returns:
            爬虫名称列表
        """
        return list(self._spiders.keys())

    # ==================== 手动触发 ====================

    async def run_spider(self, spider_name: str) -> SpiderResult:
        """
        手动触发单个爬虫运行

        Args:
            spider_name: 爬虫名称

        Returns:
            SpiderResult 运行结果

        Raises:
            ValueError: 爬虫不存在时
        """
        spider = self.get_spider(spider_name)
        if spider is None:
            raise ValueError(f"爬虫 '{spider_name}' 未注册，可用爬虫: {self.list_spiders()}")

        logger.info("[调度器] 手动触发爬虫: %s", spider_name)
        return await spider.run()

    async def run_all(self) -> list[SpiderResult]:
        """
        运行所有已注册的爬虫

        Returns:
            SpiderResult 列表
        """
        logger.info("[调度器] 开始运行所有爬虫（共 %d 个）", len(self._spiders))

        results = []
        for spider_name, spider in self._spiders.items():
            try:
                result = await spider.run()
                results.append(result)
            except Exception as e:
                logger.error("[调度器] 爬虫 %s 运行异常: %s", spider_name, str(e))
                results.append(SpiderResult(
                    spider_name=spider_name,
                    success=False,
                    error_message=str(e),
                ))

        # 打印汇总
        self._print_summary(results)
        return results

    async def run_selected(self, spider_names: list[str]) -> list[SpiderResult]:
        """
        运行指定的多个爬虫

        Args:
            spider_names: 爬虫名称列表

        Returns:
            SpiderResult 列表
        """
        logger.info("[调度器] 运行指定爬虫: %s", spider_names)

        results = []
        for name in spider_names:
            try:
                result = await self.run_spider(name)
                results.append(result)
            except Exception as e:
                logger.error("[调度器] 爬虫 %s 不存在或运行失败: %s", name, str(e))
                results.append(SpiderResult(
                    spider_name=name,
                    success=False,
                    error_message=str(e),
                ))

        self._print_summary(results)
        return results

    # ==================== 定时运行 ====================

    async def start_scheduled(self) -> None:
        """
        启动定时调度
        按照配置的时间间隔循环运行所有爬虫
        """
        interval_hours = settings.SCHEDULE_INTERVAL_HOURS
        if interval_hours <= 0:
            logger.info("[调度器] 定时运行未启用（SCHEDULE_INTERVAL_HOURS=%d）", interval_hours)
            return

        self._running = True
        interval_seconds = interval_hours * 3600

        logger.info(
            "[调度器] 定时调度已启动，间隔: %d 小时 (%d 秒)",
            interval_hours, interval_seconds
        )

        while self._running:
            try:
                logger.info("[调度器] 定时任务触发 - %s", datetime.now().isoformat())
                await self.run_all()
            except Exception as e:
                logger.error("[调度器] 定时任务执行异常: %s", str(e), exc_info=True)

            # 等待下一个周期
            logger.info("[调度器] 下次运行时间: %d 小时后", interval_hours)
            await asyncio.sleep(interval_seconds)

    def stop_scheduled(self) -> None:
        """停止定时调度"""
        self._running = False
        if self._scheduled_task and not self._scheduled_task.done():
            self._scheduled_task.cancel()
        logger.info("[调度器] 定时调度已停止")

    # ==================== 汇总报告 ====================

    @staticmethod
    def _print_summary(results: list[SpiderResult]) -> None:
        """
        打印运行结果汇总

        Args:
            results: SpiderResult 列表
        """
        total_items = sum(r.items_count for r in results)
        total_saved = sum(r.saved_count for r in results)
        total_filtered = sum(r.filtered_count for r in results)
        total_duplicates = sum(r.duplicate_count for r in results)
        total_errors = sum(r.error_count for r in results)
        total_duration = sum(r.duration for r in results)
        success_count = sum(1 for r in results if r.success)

        logger.info("=" * 60)
        logger.info("[调度器] 运行结果汇总")
        logger.info("  [引擎] %s", scheduler._engine_label)
        logger.info("=" * 60)
        logger.info("  爬虫总数: %d | 成功: %d | 失败: %d",
                     len(results), success_count, len(results) - success_count)
        logger.info("  采集条数: %d | 过滤: %d | 去重: %d | 入库: %d",
                     total_items, total_filtered, total_duplicates, total_saved)
        logger.info("  错误数量: %d | 总耗时: %.2f 秒", total_errors, total_duration)
        logger.info("-" * 60)

        for result in results:
            status = "成功" if result.success else "失败"
            logger.info(
                "  [%s] %s - 采集: %d, 入库: %d, 耗时: %.2fs (%s)",
                result.spider_name, status,
                result.items_count, result.saved_count,
                result.duration, status
            )
            if result.error_message:
                logger.info("    错误: %s", result.error_message)

        logger.info("=" * 60)


def create_scheduler() -> SpiderScheduler:
    """
    创建并配置调度器实例
    注册所有可用的爬虫

    Returns:
        配置好的 SpiderScheduler 实例
    """
    scheduler = SpiderScheduler()

    # 注册 GitHub Trending 爬虫
    if settings.ENABLE_GITHUB_TRENDING:
        from spiders.github.trending import GitHubTrendingSpider
        scheduler.register(GitHubTrendingSpider())

    # 注册 Hacker News 爬虫
    if settings.ENABLE_HACKERNEWS:
        from spiders.hackernews.hot import HackerNewsSpider
        scheduler.register(HackerNewsSpider())

    # 注册 Kaggle 比赛爬虫
    if settings.ENABLE_KAGGLE:
        from spiders.competitions.kaggle import KaggleSpider
        scheduler.register(KaggleSpider())

    # 注册 OpenAI 开发者计划爬虫
    if settings.ENABLE_OPENAI:
        from spiders.developer_programs.openai import OpenAISpider
        scheduler.register(OpenAISpider())

    # 注册天池比赛爬虫
    if settings.ENABLE_TIANCHI:
        from spiders.competitions.tianchi import TianchiSpider
        scheduler.register(TianchiSpider())

    # 注册 V2EX 爬虫
    if settings.ENABLE_V2EX:
        from spiders.forums.v2ex import V2EXSpider
        scheduler.register(V2EXSpider())

    # 注册掘金 AI 标签爬虫
    if settings.ENABLE_JUEJIN:
        from spiders.forums.juejin import JuejinSpider
        scheduler.register(JuejinSpider())

    logger.info("调度器初始化完成，已注册 %d 个爬虫: %s",
                len(scheduler.list_spiders()), scheduler.list_spiders())
    logger.info("当前引擎: %s", scheduler._engine_label)

    return scheduler
