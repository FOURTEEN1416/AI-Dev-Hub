"""
V2EX AI话题爬虫
爬取 V2EX AI 相关节点，提取帖子信息
"""

import re
import logging
from typing import Optional
from datetime import datetime

from spiders.base import BaseSpider
from spiders.models import OpportunityItem
from spiders.pipeline import DataPipeline

logger = logging.getLogger(__name__)

# V2EX AI 相关节点 URL
V2EX_URLS = [
    "https://www.v2ex.com/go/ai",
    "https://www.v2ex.com/go/chatgpt",
]


class V2EXSpider(BaseSpider):
    """
    V2EX AI话题爬虫

    目标URL: https://www.v2ex.com/go/ai, https://www.v2ex.com/go/chatgpt
    数据类型: community
    来源: V2EX

    解析内容:
    - 帖子标题
    - 帖子链接
    - 作者
    - 回复数
    - 发布时间

    注意事项:
    - V2EX 有反爬，需要设置合适的请求头
    - 控制请求频率
    - 处理验证码情况
    """

    name = "v2ex"

    def __init__(self):
        super().__init__()
        self.pipeline = DataPipeline(self)

    def _build_default_headers(self) -> dict:
        """
        构建 V2EX 专用请求头
        V2EX 对请求头比较敏感，需要模拟真实浏览器
        """
        headers = super()._build_default_headers()
        # 添加 V2EX 需要的额外请求头
        headers.update({
            "Referer": "https://www.v2ex.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        })
        return headers

    async def parse(self) -> list[OpportunityItem]:
        """
        解析 V2EX AI 节点页面

        Returns:
            OpportunityItem 列表
        """
        logger.info("[%s] 开始爬取 V2EX AI 节点", self.name)

        all_items = []
        seen_urls = set()

        for url in V2EX_URLS:
            logger.info("[%s] 爬取节点: %s", self.name, url)

            try:
                items = await self._parse_node_page(url)

                # 去重
                for item in items:
                    if item.source_url not in seen_urls:
                        seen_urls.add(item.source_url)
                        all_items.append(item)

            except Exception as e:
                logger.error("[%s] 爬取节点失败: %s (%s)", self.name, url, str(e))
                self.error_count += 1

            # V2EX 需要更长的延迟，避免触发反爬
            await self._random_delay()
            await self._random_delay()  # 额外延迟

        logger.info("[%s] 共采集到 %d 条帖子", self.name, len(all_items))
        return all_items

    async def _parse_node_page(self, url: str) -> list[OpportunityItem]:
        """
        解析单个节点页面

        Args:
            url: 节点页面 URL

        Returns:
            OpportunityItem 列表
        """
        response = await self.fetch(url)

        if response is None:
            logger.error("[%s] 无法获取页面: %s", self.name, url)
            return []

        # 检查是否遇到验证码
        if "验证码" in response.text or "captcha" in response.text.lower():
            logger.warning("[%s] 遇到验证码，跳过本次请求: %s", self.name, url)
            return []

        soup = self.parse_html(response.text)

        # V2EX 帖子列表选择器
        topic_items = soup.select(".cell.item")

        if not topic_items:
            # 尝试其他选择器
            topic_items = soup.select("div.cell")

        if not topic_items:
            logger.warning("[%s] 未找到帖子条目", self.name)
            return []

        logger.info("[%s] 找到 %d 个帖子", self.name, len(topic_items))

        items = []
        for topic_elem in topic_items:
            try:
                item = self._parse_topic_element(topic_elem)
                if item is not None:
                    items.append(item)
            except Exception as e:
                logger.debug("[%s] 解析帖子条目失败: %s", self.name, str(e))

        return items

    def _parse_topic_element(self, element) -> Optional[OpportunityItem]:
        """
        解析单个帖子元素

        Args:
            element: BeautifulSoup 元素

        Returns:
            OpportunityItem 或 None
        """
        # 提取标题和链接
        title_elem = element.select_one(".topic-link")
        if not title_elem:
            title_elem = element.select_one("a[href*='/t/']")

        if not title_elem:
            return None

        title = self.pipeline.clean_text(title_elem.get_text(strip=True))
        href = title_elem.get("href", "")

        if not title or not href:
            return None

        # 构建完整 URL
        if href.startswith("/"):
            source_url = f"https://www.v2ex.com{href}"
        elif href.startswith("http"):
            source_url = href
        else:
            return None

        # 提取作者
        author = None
        author_elem = element.select_one(".topic_info strong a")
        if author_elem:
            author = self.pipeline.clean_text(author_elem.get_text(strip=True))
        else:
            # 尝试其他选择器
            author_elem = element.select_one("a[href*='/member/']")
            if author_elem:
                author = self.pipeline.clean_text(author_elem.get_text(strip=True))

        # 提取回复数
        reply_count = None
        reply_elem = element.select_one(".count_livid, .count_orange")
        if reply_elem:
            reply_text = self.pipeline.clean_text(reply_elem.get_text(strip=True))
            try:
                reply_count = int(reply_text)
            except ValueError:
                pass
        else:
            # 尝试从文本中提取
            full_text = element.get_text()
            match = re.search(r"(\d+)\s*条回复", full_text)
            if match:
                reply_count = int(match.group(1))

        # 提取发布时间
        published_at = None
        time_elem = element.select_one(".topic_info span")
        if time_elem:
            time_text = self.pipeline.clean_text(time_elem.get_text(strip=True))
            published_at = self._parse_time(time_text)

        # 提取节点名称
        node_name = None
        node_elem = element.select_one(".node")
        if node_elem:
            node_name = self.pipeline.clean_text(node_elem.get_text(strip=True))

        # 构建标签
        tags = ["V2EX", "AI"]
        if node_name:
            tags.append(node_name)

        # 构建描述
        description = f"作者: {author}" if author else ""
        if reply_count is not None:
            description += f" | 回复: {reply_count}"

        # 提取外部 ID
        external_id = None
        match = re.search(r"/t/(\d+)", source_url)
        if match:
            external_id = match.group(1)

        # 构建元数据
        metadata = {
            "platform": "V2EX",
            "author": author,
            "reply_count": reply_count,
            "node": node_name,
            "published_at": published_at.isoformat() if published_at else None,
        }

        return OpportunityItem(
            title=title,
            description=description,
            source_url=source_url,
            source="V2EX",
            type="community",
            tags=tags,
            external_id=external_id,
            metadata=metadata,
        )

    @staticmethod
    def _parse_time(text: str) -> Optional[datetime]:
        """
        解析 V2EX 时间格式

        Args:
            text: 时间字符串，如 "10 小时前", "2 天前"

        Returns:
            datetime 对象或 None
        """
        if not text:
            return None

        now = datetime.now()

        # 处理相对时间
        if "秒前" in text:
            match = re.search(r"(\d+)", text)
            if match:
                seconds = int(match.group(1))
                return now - __import__("datetime").timedelta(seconds=seconds)

        if "分钟前" in text:
            match = re.search(r"(\d+)", text)
            if match:
                minutes = int(match.group(1))
                return now - __import__("datetime").timedelta(minutes=minutes)

        if "小时前" in text:
            match = re.search(r"(\d+)", text)
            if match:
                hours = int(match.group(1))
                return now - __import__("datetime").timedelta(hours=hours)

        if "天前" in text:
            match = re.search(r"(\d+)", text)
            if match:
                days = int(match.group(1))
                return now - __import__("datetime").timedelta(days=days)

        # 尝试解析绝对时间
        date_formats = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%m-%d %H:%M",
        ]

        for fmt in date_formats:
            try:
                parsed = datetime.strptime(text.strip(), fmt)
                # 如果只有月日，补充年份
                if parsed.year == 1900:
                    parsed = parsed.replace(year=now.year)
                return parsed
            except ValueError:
                continue

        return None
