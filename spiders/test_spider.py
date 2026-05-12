"""测试单个爬虫运行"""
import asyncio
import sys

sys.path.insert(0, '.')
from spiders.github.trending import GitHubTrendingSpider


async def main():
    s = GitHubTrendingSpider()
    items = await s.parse()
    print(f"Got {len(items)} items")
    for it in items[:5]:
        print(f"  - {it.title} ({it.source}) type={it.type}")


asyncio.run(main())
