"""
爬虫服务入口脚本
支持命令行参数指定运行某个爬虫或全部爬虫

用法:
    python run.py --all              # 运行所有爬虫
    python run.py --spider github    # 运行指定爬虫
    python run.py --spider hackernews --spider kaggle  # 运行多个指定爬虫
    python run.py --list             # 列出所有可用爬虫
    python run.py --schedule         # 启动定时调度模式
"""

import argparse
import asyncio
import logging
import sys

from spiders.scheduler import create_scheduler
from spiders.config import settings


def setup_logging() -> None:
    """配置日志"""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # 降低第三方库的日志级别
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("fake_useragent").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="AI Dev Hub 爬虫服务",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run.py --all                              运行所有爬虫
  python run.py --spider github_trending           运行 GitHub Trending 爬虫
  python run.py --spider hackernews                运行 Hacker News 爬虫
  python run.py --spider kaggle                    运行 Kaggle 爬虫
  python run.py --spider openai                    运行 OpenAI 爬虫
  python run.py --spider github_trending --spider hackernews  运行多个爬虫
  python run.py --list                             列出所有可用爬虫
  python run.py --schedule                         启动定时调度模式
        """,
    )

    parser.add_argument(
        "--spider",
        type=str,
        action="append",
        dest="spiders",
        help="指定要运行的爬虫名称（可多次使用以运行多个爬虫）",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="run_all",
        help="运行所有已注册的爬虫",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_spiders",
        help="列出所有可用的爬虫",
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        dest="run_schedule",
        help="启动定时调度模式",
    )

    return parser.parse_args()


async def main() -> None:
    """主入口函数"""
    setup_logging()
    logger = logging.getLogger(__name__)

    args = parse_args()
    scheduler = create_scheduler()

    # 列出爬虫
    if args.list_spiders:
        spiders = scheduler.list_spiders()
        logger.info("可用爬虫列表:")
        for name in spiders:
            logger.info("  - %s", name)
        return

    # 定时调度模式
    if args.run_schedule:
        logger.info("启动定时调度模式...")
        try:
            await scheduler.start_scheduled()
        except (KeyboardInterrupt, asyncio.CancelledError):
            logger.info("收到中断信号，停止调度...")
            scheduler.stop_scheduled()
        return

    # 运行指定爬虫
    if args.spiders:
        spider_names = args.spiders
        # 验证爬虫是否存在
        available = scheduler.list_spiders()
        for name in spider_names:
            if name not in available:
                logger.error("爬虫 '%s' 不存在，可用爬虫: %s", name, available)
                sys.exit(1)
        results = await scheduler.run_selected(spider_names)
        _exit_with_results(results)
        return

    # 运行所有爬虫
    if args.run_all:
        results = await scheduler.run_all()
        _exit_with_results(results)
        return

    # 未指定参数，显示帮助
    logger.info("未指定运行参数，使用 --help 查看帮助信息")


def _exit_with_results(results: list) -> None:
    """根据运行结果设置退出码"""
    from spiders.models import SpiderResult
    has_error = any(not r.success for r in results)
    sys.exit(1 if has_error else 0)


if __name__ == "__main__":
    asyncio.run(main())
