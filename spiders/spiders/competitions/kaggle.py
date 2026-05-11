"""
Kaggle 比赛爬虫
爬取 Kaggle Competitions 页面，提取比赛信息
"""

import re
import logging
from typing import Optional
from datetime import datetime

from spiders.base import BaseSpider
from spiders.models import OpportunityItem
from spiders.pipeline import DataPipeline

logger = logging.getLogger(__name__)

# Kaggle 比赛页面 URL
KAGGLE_COMPETITIONS_URL = "https://www.kaggle.com/competitions"

# AI 相关标签关键词
AI_COMPETITION_KEYWORDS = [
    "ai", "ml", "machine learning", "deep learning",
    "nlp", "computer vision", "image", "text",
    "tabular", "classification", "regression",
    "detection", "segmentation", "generation",
    "reinforcement", "recommendation", "forecasting",
    "neural", "transformer", "bert", "gpt",
    "llm", "language model", "speech", "audio",
    "video", "3d", "point cloud", "graph",
    "time series", "anomaly detection",
]


class KaggleSpider(BaseSpider):
    """
    Kaggle 比赛爬虫
    爬取 Kaggle Competitions 页面，提取比赛信息
    """

    name = "kaggle"

    def __init__(self):
        super().__init__()
        self.pipeline = DataPipeline(self)

    async def parse(self) -> list[OpportunityItem]:
        """
        解析 Kaggle 比赛页面

        Returns:
            OpportunityItem 列表
        """
        logger.info("[%s] 开始爬取 Kaggle 比赛页面", self.name)

        all_items = []

        # 爬取不同状态的比赛
        categories = [
            {"url": KAGGLE_COMPETITIONS_URL, "label": "all"},
            {"url": f"{KAGGLE_COMPETITIONS_URL}?search=AI", "label": "ai_search"},
            {"url": f"{KAGGLE_COMPETITIONS_URL}?search=machine+learning", "label": "ml_search"},
        ]

        seen_urls = set()

        for category in categories:
            logger.info("[%s] 爬取分类: %s", self.name, category["label"])
            items = await self._parse_competitions_page(category["url"], category["label"])

            # 去重
            for item in items:
                if item.source_url not in seen_urls:
                    seen_urls.add(item.source_url)
                    all_items.append(item)

            await self._random_delay()

        logger.info("[%s] 共采集到 %d 个比赛", self.name, len(all_items))
        return all_items

    async def _parse_competitions_page(self, url: str, category: str) -> list[OpportunityItem]:
        """
        解析比赛列表页面

        Args:
            url: 比赛页面 URL
            category: 分类标签

        Returns:
            OpportunityItem 列表
        """
        response = await self.fetch(url)
        if response is None:
            logger.error("[%s] 无法获取比赛页面: %s", self.name, url)
            return []

        soup = self.parse_html(response.text)

        # Kaggle 比赛列表的选择器
        # Kaggle 使用 React 渲染，尝试多种选择器
        competition_items = []

        # 尝试选择器 1：基于 data-testid 属性
        list_items = soup.select("[data-testid='competition-list-item']")
        if not list_items:
            # 尝试选择器 2：基于 CSS 类名
            list_items = soup.select("div.sc-hLclGa, div.competition-item")

        if not list_items:
            # 尝试选择器 3：基于链接
            links = soup.select("a[href*='/competitions/']")
            if links:
                list_items = links

        if not list_items:
            logger.warning("[%s] 未找到比赛条目（页面可能需要 JavaScript 渲染）", self.name)
            # 尝试从页面中提取所有比赛链接
            all_links = soup.select("a")
            comp_links = [
                a for a in all_links
                if a.get("href", "").startswith("/competitions/")
                and a.get("href", "").count("/") == 2
            ]
            if comp_links:
                logger.info("[%s] 找到 %d 个比赛链接，尝试逐个访问", self.name, len(comp_links))
                for link in comp_links[:20]:  # 限制数量
                    href = link.get("href", "")
                    full_url = f"https://www.kaggle.com{href}"
                    item = await self._parse_competition_detail(full_url)
                    if item is not None:
                        competition_items.append(item)
                    await self._random_delay()
            return competition_items

        for item_elem in list_items:
            try:
                item = self._parse_competition_element(item_elem)
                if item is not None:
                    competition_items.append(item)
            except Exception as e:
                logger.error("[%s] 解析比赛条目失败: %s", self.name, str(e))
                self.error_count += 1

        return competition_items

    def _parse_competition_element(self, element) -> Optional[OpportunityItem]:
        """
        解析单个比赛元素

        Args:
            element: BeautifulSoup 元素

        Returns:
            OpportunityItem 或 None
        """
        # 提取标题和链接
        link_elem = element.select_one("a") if element.name != "a" else element
        if link_elem:
            href = link_elem.get("href", "")
            title = self.pipeline.clean_text(link_elem.get_text(strip=True))
        else:
            return None

        if not href or not title:
            return None

        # 构建完整 URL
        if href.startswith("/"):
            source_url = f"https://www.kaggle.com{href}"
        elif href.startswith("http"):
            source_url = href
        else:
            return None

        # 提取描述
        description = ""
        desc_elem = element.select_one("p, .competition-description, [data-testid='competition-description']")
        if desc_elem:
            description = self.pipeline.clean_text(desc_elem.get_text(strip=True))

        # 提取截止日期
        deadline = None
        deadline_elem = element.select_one(
            "time, .competition-deadline, [data-testid='competition-deadline']"
        )
        if deadline_elem:
            deadline_text = self.pipeline.clean_text(deadline_elem.get_text(strip=True))
            deadline = self._parse_deadline(deadline_text)

        # 提取奖励
        reward = None
        reward_elem = element.select_one(
            ".competition-reward, [data-testid='competition-reward'], .prize"
        )
        if reward_elem:
            reward = self.pipeline.clean_text(reward_elem.get_text(strip=True))
        else:
            # 尝试从文本中提取奖励信息
            full_text = element.get_text(strip=True).lower()
            reward_match = re.search(r"\$[\d,]+", full_text)
            if reward_match:
                reward = reward_match.group(0)

        # 提取标签
        tags = ["Kaggle", "Competition"]
        tag_elems = element.select(".tag, .competition-tag, [data-testid='competition-tag']")
        for tag_elem in tag_elems:
            tag_text = self.pipeline.clean_text(tag_elem.get_text(strip=True))
            if tag_text:
                tags.append(tag_text)

        # 补充 AI 相关标签
        combined_text = f"{title} {description}".lower()
        for keyword in AI_COMPETITION_KEYWORDS:
            if keyword in combined_text and keyword.title() not in tags:
                tags.append(keyword.title())

        # 提取外部 ID
        external_id = None
        match = re.search(r"/competitions/([^/?]+)", source_url)
        if match:
            external_id = match.group(1)

        # 构建元数据
        metadata = {
            "category": "kaggle",
            "platform": "Kaggle",
        }

        return OpportunityItem(
            title=title,
            description=description or "Kaggle 数据科学竞赛",
            source_url=source_url,
            source="Kaggle",
            type="competition",
            tags=tags,
            external_id=external_id,
            reward=reward,
            deadline=deadline,
            metadata=metadata,
        )

    async def _parse_competition_detail(self, url: str) -> Optional[OpportunityItem]:
        """
        解析比赛详情页面

        Args:
            url: 比赛详情页 URL

        Returns:
            OpportunityItem 或 None
        """
        response = await self.fetch(url)
        if response is None:
            return None

        soup = self.parse_html(response.text)

        # 提取标题
        title_elem = soup.select_one("h1, h2, .competition-title")
        title = ""
        if title_elem:
            title = self.pipeline.clean_text(title_elem.get_text(strip=True))
        if not title:
            # 从 URL 中提取
            match = re.search(r"/competitions/([^/?]+)", url)
            if match:
                title = match.group(1).replace("-", " ").title()

        # 提取描述
        description = ""
        desc_elem = soup.select_one(
            ".competition-description, .markdown-converter, [data-testid='markdown-container']"
        )
        if desc_elem:
            description = self.pipeline.clean_text(desc_elem.get_text(strip=True))[:500]

        # 提取截止日期
        deadline = None
        deadline_elem = soup.select_one("time, .competition-deadline")
        if deadline_elem:
            deadline_text = self.pipeline.clean_text(deadline_elem.get_text(strip=True))
            deadline = self._parse_deadline(deadline_text)
            # 尝试 datetime 属性
            datetime_attr = deadline_elem.get("datetime", "")
            if datetime_attr:
                deadline = self._parse_deadline(datetime_attr)

        # 提取奖励
        reward = None
        full_text = soup.get_text(strip=True).lower()
        reward_match = re.search(r"\$[\d,]+(?:\s*-\s*\$[\d,]+)?", full_text)
        if reward_match:
            reward = reward_match.group(0)

        # 提取标签
        tags = ["Kaggle", "Competition"]
        tag_elems = soup.select(".tag, .competition-tag")
        for tag_elem in tag_elems:
            tag_text = self.pipeline.clean_text(tag_elem.get_text(strip=True))
            if tag_text:
                tags.append(tag_text)

        # 提取外部 ID
        external_id = None
        match = re.search(r"/competitions/([^/?]+)", url)
        if match:
            external_id = match.group(1)

        return OpportunityItem(
            title=title,
            description=description or "Kaggle 数据科学竞赛",
            source_url=url,
            source="Kaggle",
            type="competition",
            tags=tags,
            external_id=external_id,
            reward=reward,
            deadline=deadline,
            metadata={"category": "kaggle", "platform": "Kaggle"},
        )

    @staticmethod
    def _parse_deadline(text: str):
        """
        解析截止日期字符串

        Args:
            text: 日期字符串

        Returns:
            date 对象或 None
        """
        if not text:
            return None

        # 尝试多种日期格式
        date_formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
            "%m/%d/%Y",
            "%Y/%m/%d",
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(text.strip(), fmt).date()
            except ValueError:
                continue

        return None
