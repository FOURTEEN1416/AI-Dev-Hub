"""
掘金 AI 标签文章爬虫
爬取掘金 AI 和 ChatGPT 标签下的文章，提取文章信息
"""

import re
import logging
from typing import Optional
from datetime import datetime

from spiders.base import BaseSpider
from spiders.models import OpportunityItem
from spiders.pipeline import DataPipeline

logger = logging.getLogger(__name__)

# 掘金标签页面 URL
JUEJIN_TAG_URLS = [
    ("AI", "https://juejin.cn/tag/AI"),
    ("ChatGPT", "https://juejin.cn/tag/ChatGPT"),
]

# 掘金 API 端点
JUEJIN_API_URL = "https://api.juejin.cn/recommend_api/v1/article/recommend_cate_feed"


class JuejinSpider(BaseSpider):
    """
    掘金 AI 标签文章爬虫

    目标URL: https://juejin.cn/tag/AI, https://juejin.cn/tag/ChatGPT
    数据类型: community
    来源: 掘金

    解析内容:
    - 文章标题
    - 文章链接
    - 作者
    - 点赞数、评论数
    - 发布时间

    注意事项:
    - 掘金是 SPA，需要 CloakBrowser 或分析 API
    - 优先使用 API 方式（如果有公开 API）
    - 处理动态加载
    """

    name = "juejin"

    def __init__(self):
        super().__init__()
        self.pipeline = DataPipeline(self)

    async def parse(self) -> list[OpportunityItem]:
        """
        解析掘金 AI 标签页面

        Returns:
            OpportunityItem 列表
        """
        logger.info("[%s] 开始爬取掘金 AI 标签", self.name)

        all_items = []
        seen_urls = set()

        # 尝试使用 API 方式
        try:
            items = await self._parse_via_api()
            for item in items:
                if item.source_url not in seen_urls:
                    seen_urls.add(item.source_url)
                    all_items.append(item)
        except Exception as e:
            logger.warning("[%s] API 方式失败，尝试 CloakBrowser: %s", self.name, str(e))

            # 回退到 CloakBrowser 方式
            for tag_name, url in JUEJIN_TAG_URLS:
                try:
                    items = await self._parse_with_playwright(url, tag_name)
                    for item in items:
                        if item.source_url not in seen_urls:
                            seen_urls.add(item.source_url)
                            all_items.append(item)
                except Exception as e:
                    logger.error("[%s] 爬取标签 %s 失败: %s", self.name, tag_name, str(e))
                    self.error_count += 1

                await self._random_delay()

        logger.info("[%s] 共采集到 %d 篇文章", self.name, len(all_items))
        return all_items

    async def _parse_via_api(self) -> list[OpportunityItem]:
        """
        通过掘金 API 获取文章列表

        Returns:
            OpportunityItem 列表
        """
        items = []

        # 掘金的分类 ID
        # AI 相关分类: 前端(6)、后端(7)、人工智能(11)
        category_ids = [11]  # 人工智能分类

        for category_id in category_ids:
            # 构建请求体
            payload = {
                "id_type": 2,
                "sort_type": 200,  # 热门排序
                "cate_id": category_id,
                "cursor": "0",
                "limit": 20,
            }

            headers = self._build_default_headers()
            headers.update({
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Origin": "https://juejin.cn",
                "Referer": "https://juejin.cn/",
            })

            try:
                response = await self.client.post(
                    JUEJIN_API_URL,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

                if data.get("err_no") != 0:
                    logger.warning("[%s] API 返回错误: %s", self.name, data.get("err_msg"))
                    continue

                article_list = data.get("data", [])

                for article in article_list:
                    item = self._parse_api_article(article)
                    if item is not None:
                        items.append(item)

            except Exception as e:
                logger.error("[%s] API 请求失败: %s", self.name, str(e))
                raise

        return items

    def _parse_api_article(self, article: dict) -> Optional[OpportunityItem]:
        """
        解析 API 返回的文章数据

        Args:
            article: 文章数据字典

        Returns:
            OpportunityItem 或 None
        """
        try:
            article_id = article.get("article_id") or article.get("id")
            title = article.get("title", "")

            if not title or not article_id:
                return None

            # 构建文章 URL
            source_url = f"https://juejin.cn/post/{article_id}"

            # 提取作者
            author_info = article.get("author_user_info", {})
            author = author_info.get("user_name", "")

            # 提取统计数据
            digg_count = article.get("article_info", {}).get("digg_count", 0)
            comment_count = article.get("article_info", {}).get("comment_count", 0)
            view_count = article.get("article_info", {}).get("view_count", 0)

            # 提取发布时间
            published_at = None
            ctime = article.get("article_info", {}).get("ctime")
            if ctime:
                try:
                    published_at = datetime.fromtimestamp(int(ctime))
                except (ValueError, TypeError):
                    pass

            # 提取标签
            tags = ["掘金", "AI"]
            tag_list = article.get("tags", [])
            for tag in tag_list[:3]:  # 最多取3个标签
                tag_name = tag.get("tag_name", "")
                if tag_name:
                    tags.append(tag_name)

            # 构建描述
            description = f"作者: {author}" if author else ""
            if digg_count:
                description += f" | 点赞: {digg_count}"
            if comment_count:
                description += f" | 评论: {comment_count}"

            # 构建元数据
            metadata = {
                "platform": "掘金",
                "author": author,
                "digg_count": digg_count,
                "comment_count": comment_count,
                "view_count": view_count,
                "published_at": published_at.isoformat() if published_at else None,
            }

            return OpportunityItem(
                title=title,
                description=description,
                source_url=source_url,
                source="掘金",
                type="community",
                tags=tags,
                external_id=str(article_id),
                metadata=metadata,
            )

        except Exception as e:
            logger.debug("[%s] 解析文章数据失败: %s", self.name, str(e))
            return None

    async def _parse_with_playwright(self, url: str, tag_name: str) -> list[OpportunityItem]:
        """
        使用 CloakBrowser 渲染并解析页面（Playwright 兼容接口）

        Args:
            url: 标签页面 URL
            tag_name: 标签名称

        Returns:
            OpportunityItem 列表
        """
        from cloakbrowser import launch_async

        items = []
        browser = None
        try:
            browser = await launch_async(
                headless=True,
                stealth_args=True,
                humanize=True,
            )
            context = await browser.new_context(
                user_agent=self._get_random_ua(),
            )
            page = await context.new_page()

            logger.info("[%s] CloakBrowser 正在加载页面: %s", self.name, url)
            await page.goto(url, wait_until="networkidle", timeout=30000)

            # 等待文章列表加载
            await page.wait_for_selector(".item, .article-item, [class*='content-item']", timeout=15000)

            # 滚动加载更多内容
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, 1000)")
                await page.wait_for_timeout(1000)

            # 获取页面内容
            content = await page.content()
            soup = self.parse_html(content)

            # 解析文章列表
            items = self._parse_article_list(soup, tag_name)

        except Exception as e:
            logger.error("[%s] CloakBrowser 解析失败: %s", self.name, str(e))
        finally:
            if browser:
                await browser.close()

        return items

    def _parse_article_list(self, soup, tag_name: str) -> list[OpportunityItem]:
        """
        解析文章列表

        Args:
            soup: BeautifulSoup 对象
            tag_name: 标签名称

        Returns:
            OpportunityItem 列表
        """
        items = []

        # 尝试多种选择器
        article_elements = (
            soup.select(".item") or
            soup.select(".article-item") or
            soup.select("[class*='content-item']") or
            soup.select("a[href*='/post/']")
        )

        if not article_elements:
            logger.warning("[%s] 未找到文章条目", self.name)
            return items

        logger.info("[%s] 找到 %d 篇文章", self.name, len(article_elements))

        for element in article_elements:
            try:
                item = self._parse_article_element(element, tag_name)
                if item is not None:
                    items.append(item)
            except Exception as e:
                logger.debug("[%s] 解析文章条目失败: %s", self.name, str(e))

        return items

    def _parse_article_element(self, element, tag_name: str) -> Optional[OpportunityItem]:
        """
        解析单个文章元素

        Args:
            element: BeautifulSoup 元素
            tag_name: 标签名称

        Returns:
            OpportunityItem 或 None
        """
        # 提取标题和链接
        title_elem = (
            element.select_one(".title") or
            element.select_one("h2") or
            element.select_one("h3") or
            element.select_one("a[href*='/post/']")
        )

        if not title_elem:
            return None

        title = self.pipeline.clean_text(title_elem.get_text(strip=True))

        # 获取链接
        href = ""
        if element.name == "a":
            href = element.get("href", "")
        else:
            link_elem = element.select_one("a[href*='/post/']")
            if link_elem:
                href = link_elem.get("href", "")

        if not title or not href:
            return None

        # 构建完整 URL
        if href.startswith("/"):
            source_url = f"https://juejin.cn{href}"
        elif href.startswith("http"):
            source_url = href
        else:
            return None

        # 提取作者
        author = None
        author_elem = element.select_one(".author-name, .user-name, [class*='author']")
        if author_elem:
            author = self.pipeline.clean_text(author_elem.get_text(strip=True))

        # 提取点赞数
        digg_count = None
        digg_elem = element.select_one(".like-count, .digg-count, [class*='like']")
        if digg_elem:
            digg_text = self.pipeline.clean_text(digg_elem.get_text(strip=True))
            match = re.search(r"(\d+)", digg_text)
            if match:
                digg_count = int(match.group(1))

        # 提取评论数
        comment_count = None
        comment_elem = element.select_one(".comment-count, [class*='comment']")
        if comment_elem:
            comment_text = self.pipeline.clean_text(comment_elem.get_text(strip=True))
            match = re.search(r"(\d+)", comment_text)
            if match:
                comment_count = int(match.group(1))

        # 构建标签
        tags = ["掘金", tag_name]

        # 构建描述
        description = f"作者: {author}" if author else ""
        if digg_count:
            description += f" | 点赞: {digg_count}"
        if comment_count:
            description += f" | 评论: {comment_count}"

        # 提取外部 ID
        external_id = None
        match = re.search(r"/post/(\d+)", source_url)
        if match:
            external_id = match.group(1)

        # 构建元数据
        metadata = {
            "platform": "掘金",
            "author": author,
            "digg_count": digg_count,
            "comment_count": comment_count,
        }

        return OpportunityItem(
            title=title,
            description=description,
            source_url=source_url,
            source="掘金",
            type="community",
            tags=tags,
            external_id=external_id,
            metadata=metadata,
        )
