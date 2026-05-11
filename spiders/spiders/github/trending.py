"""
GitHub Trending 爬虫
爬取 GitHub Trending 页面，过滤 AI/ML 相关仓库，提取仓库信息
"""

import re
import logging
from typing import Optional

from spiders.base import BaseSpider
from spiders.models import OpportunityItem
from spiders.pipeline import DataPipeline

logger = logging.getLogger(__name__)

# AI/ML 相关关键词，用于过滤仓库
AI_ML_KEYWORDS = [
    "ai", "ml", "llm", "gpt", "transformer",
    "machine-learning", "deep-learning", "neural-network",
    "nlp", "computer-vision", "diffusion", "stable-diffusion",
    "generative", "chatbot", "langchain", "openai", "anthropic",
    "embedding", "vector-database", "rag", "retrieval-augmented",
    "fine-tuning", "finetune", "prompt-engineering",
    "text-generation", "image-generation", "speech-recognition",
    "object-detection", "semantic-segmentation",
    "reinforcement-learning", "transfer-learning",
    "bert", "roberta", "llama", "mistral", "claude",
    "whisper", "dalle", "midjourney", "autogpt",
    "agent", "autonomous-agent", "multi-modal",
    "vision-transformer", "vit", "sora",
    "machine learning", "deep learning", "neural network",
    "large language model", "large language models",
]


class GitHubTrendingSpider(BaseSpider):
    """
    GitHub Trending 爬虫
    爬取 https://github.com/trending 页面，提取 AI/ML 相关的 Trending 仓库
    """

    name = "github_trending"

    # Trending 页面 URL，支持按时间范围筛选
    TRENDING_URL = "https://github.com/trending"

    def __init__(self):
        super().__init__()
        self.pipeline = DataPipeline(self)

    async def parse(self) -> list[OpportunityItem]:
        """
        解析 GitHub Trending 页面

        Returns:
            AI/ML 相关的 OpportunityItem 列表
        """
        logger.info("[%s] 开始爬取 GitHub Trending 页面", self.name)

        # 分别爬取 daily、weekly、monthly 的 trending
        all_items = []
        time_ranges = ["daily", "weekly", "monthly"]

        for time_range in time_ranges:
            logger.info("[%s] 爬取 %s trending...", self.name, time_range)
            url = f"{self.TRENDING_URL}?since={time_range}"
            items = await self._parse_trending_page(url, time_range)
            all_items.extend(items)
            await self._random_delay()

        logger.info("[%s] 共采集到 %d 条 AI/ML 相关仓库", self.name, len(all_items))
        return all_items

    async def _parse_trending_page(self, url: str, time_range: str) -> list[OpportunityItem]:
        """
        解析单个 Trending 页面

        Args:
            url: Trending 页面 URL
            time_range: 时间范围（daily/weekly/monthly）

        Returns:
            解析后的 OpportunityItem 列表
        """
        response = await self.fetch(url)
        if response is None:
            logger.error("[%s] 无法获取 Trending 页面: %s", self.name, url)
            return []

        soup = self.parse_html(response.text)
        articles = soup.select("article.Box-row")

        if not articles:
            logger.warning("[%s] 未找到 Trending 仓库条目", self.name)
            return []

        logger.info("[%s] 找到 %d 个 Trending 仓库", self.name, len(articles))

        items = []
        for article in articles:
            try:
                item = self._parse_repository(article, time_range)
                if item is not None:
                    items.append(item)
            except Exception as e:
                logger.error("[%s] 解析仓库条目失败: %s", self.name, str(e))
                self.error_count += 1

        return items

    def _parse_repository(self, article, time_range: str) -> Optional[OpportunityItem]:
        """
        解析单个仓库条目

        Args:
            article: BeautifulSoup 的 article 元素
            time_range: 时间范围

        Returns:
            OpportunityItem 或 None（非 AI/ML 仓库时）
        """
        # 提取仓库名
        repo_name_elem = article.select_one("h2 a")
        if not repo_name_elem:
            return None

        repo_name = self.pipeline.clean_text(repo_name_elem.get_text(strip=True).replace("/", " / "))
        repo_href = repo_name_elem.get("href", "")
        repo_url = f"https://github.com{repo_href}" if repo_href else ""

        # 提取描述
        desc_elem = article.select_one("p.color-fg-muted")
        description = ""
        if desc_elem:
            description = self.pipeline.clean_text(desc_elem.get_text(strip=True))

        # 检查是否为 AI/ML 相关仓库
        if not self._is_ai_ml_related(repo_name, description):
            self.filtered_count += 1
            return None

        # 提取编程语言
        language = None
        lang_elem = article.select_one("[itemprop='programmingLanguage']")
        if lang_elem:
            language = self.pipeline.clean_text(lang_elem.get_text(strip=True))

        # 提取总 Star 数
        stars = None
        stars_elem = article.select("a.Link--muted.d-inline-block.mr-3")
        for elem in stars_elem:
            href = elem.get("href", "")
            text = self.pipeline.clean_text(elem.get_text(strip=True))
            if "/stargazers" in href:
                stars = self.pipeline.parse_star_count(text)
                break

        # 提取今日 Star 增量
        stars_today = None
        stars_today_elem = article.select_one("span.d-inline-block.float-sm-right")
        if stars_today_elem:
            today_text = self.pipeline.clean_text(stars_today_elem.get_text(strip=True))
            # 匹配 "1,234 stars today/this week/this month"
            match = re.search(r"([\d,]+)\s*stars?", today_text, re.IGNORECASE)
            if match:
                stars_today = self.pipeline.parse_star_count(match.group(1))

        # 提取 Fork 数
        forks = None
        forks_elem = article.select("a.Link--muted.d-inline-block.mr-3")
        for elem in forks_elem:
            href = elem.get("href", "")
            text = self.pipeline.clean_text(elem.get_text(strip=True))
            if "/forks" in href:
                forks = self.pipeline.parse_star_count(text)
                break

        # 提取标签（从内置话题标签）
        built_in_tags = []
        tag_elems = article.select("a.topic-tag")
        for tag_elem in tag_elems:
            tag_text = self.pipeline.clean_text(tag_elem.get_text(strip=True))
            if tag_text:
                built_in_tags.append(tag_text)

        # 自动提取标签
        tags = self._extract_tags(repo_name, description, language, built_in_tags)

        # 构建额外元数据
        metadata = {
            "time_range": time_range,
            "forks": forks,
            "repo_full_name": repo_href.lstrip("/") if repo_href else None,
        }

        return OpportunityItem(
            title=repo_name,
            description=description,
            source_url=repo_url,
            source="GitHub",
            type="community",
            tags=tags,
            external_id=repo_href.lstrip("/") if repo_href else None,
            language=language,
            stars=stars,
            stars_today=stars_today,
            metadata=metadata,
        )

    @staticmethod
    def _is_ai_ml_related(title: str, description: str) -> bool:
        """
        判断仓库是否与 AI/ML 相关

        Args:
            title: 仓库名
            description: 仓库描述

        Returns:
            True 表示 AI/ML 相关
        """
        combined_text = f"{title} {description}".lower()
        for keyword in AI_ML_KEYWORDS:
            if keyword.lower() in combined_text:
                return True
        return False

    @staticmethod
    def _extract_tags(
        title: str,
        description: str,
        language: Optional[str],
        built_in_tags: list[str],
    ) -> list[str]:
        """
        自动提取标签

        Args:
            title: 仓库名
            description: 仓库描述
            language: 编程语言
            built_in_tags: GitHub 内置话题标签

        Returns:
            标签列表
        """
        tags = set()

        # 添加编程语言标签
        if language:
            tags.add(language)

        # 添加内置话题标签
        for tag in built_in_tags:
            tags.add(tag)

        # 从标题和描述中提取 AI 相关关键词作为标签
        combined_text = f"{title} {description}".lower()

        tag_keywords = [
            "llm", "gpt", "transformer", "bert", "roberta", "llama", "mistral",
            "langchain", "rag", "embedding", "fine-tuning", "prompt",
            "diffusion", "stable-diffusion", "generative-ai",
            "computer-vision", "nlp", "speech", "agent",
            "reinforcement-learning", "multi-modal",
            "chatbot", "text-generation", "image-generation",
            "vector-database", "knowledge-graph",
        ]

        for keyword in tag_keywords:
            if keyword in combined_text:
                tags.add(keyword)

        return list(tags)
