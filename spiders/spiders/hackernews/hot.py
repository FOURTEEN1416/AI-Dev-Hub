"""
Hacker News 爬虫
使用 HN API 获取 top stories 和 new stories，过滤 AI 相关文章
"""

import logging
from typing import Optional

from spiders.base import BaseSpider
from spiders.models import OpportunityItem
from spiders.pipeline import DataPipeline

logger = logging.getLogger(__name__)

# HN API 基础地址
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"

# AI 相关关键词，用于过滤文章
AI_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "deep learning",
    "neural network", "llm", "large language model", "gpt", "chatgpt",
    "transformer", "bert", "nlp", "natural language",
    "computer vision", "image recognition", "speech recognition",
    "generative", "diffusion", "stable diffusion", "midjourney", "dall-e",
    "openai", "anthropic", "google deepmind", "deepmind",
    "langchain", "embedding", "vector database", "rag",
    "reinforcement learning", "transfer learning",
    "fine-tuning", "finetune", "prompt engineering",
    "autonomous agent", "ai agent", "multi-modal",
    "claude", "gemini", "copilot", "llama", "mistral",
    "robotics", "self-driving", "autonomous driving",
    "tensorflow", "pytorch", "jax", "hugging face",
    "foundation model", "alignment", "rlhf",
    "text-to-image", "text-to-video", "text-to-code",
    "code generation", "ai safety", "agi",
    "machine learning model", "dataset", "benchmark",
    "whisper", "sora", "stable-diffusion",
]


class HackerNewsSpider(BaseSpider):
    """
    Hacker News 爬虫
    使用 HN API 获取 top stories 和 new stories，过滤 AI 相关文章
    """

    name = "hackernews"

    # 每次获取的最大文章数量
    MAX_STORIES = 50

    def __init__(self):
        super().__init__()
        self.pipeline = DataPipeline(self)

    async def parse(self) -> list[OpportunityItem]:
        """
        解析 Hacker News 文章

        Returns:
            AI 相关的 OpportunityItem 列表
        """
        logger.info("[%s] 开始爬取 Hacker News", self.name)

        all_items = []

        # 获取 top stories
        logger.info("[%s] 获取 Top Stories...", self.name)
        top_items = await self._fetch_stories("topstories")
        all_items.extend(top_items)
        logger.info("[%s] Top Stories 中找到 %d 条 AI 相关文章", self.name, len(top_items))

        # 获取 new stories
        logger.info("[%s] 获取 New Stories...", self.name)
        new_items = await self._fetch_stories("newstories")
        all_items.extend(new_items)
        logger.info("[%s] New Stories 中找到 %d 条 AI 相关文章", self.name, len(new_items))

        # 基于 source_url 去重（top 和 new 可能有重叠）
        seen_urls = set()
        unique_items = []
        for item in all_items:
            if item.source_url not in seen_urls:
                seen_urls.add(item.source_url)
                unique_items.append(item)

        logger.info("[%s] 共采集到 %d 条 AI 相关文章（去重后）", self.name, len(unique_items))
        return unique_items

    async def _fetch_stories(self, story_type: str) -> list[OpportunityItem]:
        """
        获取指定类型的文章列表

        Args:
            story_type: 文章类型（topstories / newstories）

        Returns:
            AI 相关的 OpportunityItem 列表
        """
        # 获取文章 ID 列表
        story_ids_url = f"{HN_API_BASE}/{story_type}.json"
        story_ids = await self.fetch_json(story_ids_url)

        if not story_ids or not isinstance(story_ids, list):
            logger.warning("[%s] 无法获取 %s 文章 ID 列表", self.name, story_type)
            return []

        # 限制获取数量
        story_ids = story_ids[:self.MAX_STORIES]
        logger.info("[%s] 获取到 %d 个文章 ID", self.name, len(story_ids))

        items = []
        for idx, story_id in enumerate(story_ids):
            try:
                item = await self._fetch_story_detail(story_id, story_type)
                if item is not None:
                    items.append(item)
            except Exception as e:
                logger.error("[%s] 获取文章详情失败 (ID: %d): %s", self.name, story_id, str(e))
                self.error_count += 1

            # 每 5 个请求延迟一次
            if (idx + 1) % 5 == 0:
                await self._random_delay()

        return items

    async def _fetch_story_detail(self, story_id: int, story_type: str) -> Optional[OpportunityItem]:
        """
        获取单篇文章详情

        Args:
            story_id: 文章 ID
            story_type: 文章类型

        Returns:
            OpportunityItem 或 None（非 AI 相关时）
        """
        detail_url = f"{HN_API_BASE}/item/{story_id}.json"
        detail = await self.fetch_json(detail_url)

        if not detail or not isinstance(detail, dict):
            return None

        title = detail.get("title", "")
        url = detail.get("url", "")
        score = detail.get("score", 0)
        by = detail.get("by", "")
        time_ts = detail.get("time", 0)
        descendants = detail.get("descendants", 0)  # 评论数

        # 如果没有外部链接，使用 HN 内部链接
        if not url:
            url = f"https://news.ycombinator.com/item?id={story_id}"

        # 过滤 AI 相关文章
        if not self._is_ai_related(title):
            self.filtered_count += 1
            return None

        # 构建描述
        description = f"HN {story_type} | Score: {score} | 作者: {by} | 评论: {descendants}"

        # 提取标签
        tags = self._extract_tags(title)

        # 构建元数据
        metadata = {
            "hn_id": story_id,
            "hn_score": score,
            "hn_author": by,
            "hn_comment_count": descendants,
            "hn_timestamp": time_ts,
            "story_type": story_type,
        }

        return OpportunityItem(
            title=title,
            description=description,
            source_url=url,
            source="Hacker News",
            type="community",
            tags=tags,
            external_id=str(story_id),
            metadata=metadata,
        )

    @staticmethod
    def _is_ai_related(title: str) -> bool:
        """
        判断文章标题是否与 AI 相关

        Args:
            title: 文章标题

        Returns:
            True 表示 AI 相关
        """
        title_lower = title.lower()
        for keyword in AI_KEYWORDS:
            if keyword in title_lower:
                return True
        return False

    @staticmethod
    def _extract_tags(title: str) -> list[str]:
        """
        从标题中提取标签

        Args:
            title: 文章标题

        Returns:
            标签列表
        """
        tags = []
        title_lower = title.lower()

        tag_mapping = {
            "llm": "LLM",
            "gpt": "GPT",
            "chatgpt": "ChatGPT",
            "transformer": "Transformer",
            "bert": "BERT",
            "nlp": "NLP",
            "natural language": "NLP",
            "computer vision": "Computer Vision",
            "generative": "Generative AI",
            "diffusion": "Diffusion",
            "openai": "OpenAI",
            "anthropic": "Anthropic",
            "deepmind": "DeepMind",
            "langchain": "LangChain",
            "embedding": "Embedding",
            "rag": "RAG",
            "reinforcement learning": "Reinforcement Learning",
            "fine-tuning": "Fine-tuning",
            "finetune": "Fine-tuning",
            "prompt": "Prompt Engineering",
            "multi-modal": "Multi-modal",
            "claude": "Claude",
            "gemini": "Gemini",
            "copilot": "Copilot",
            "llama": "LLaMA",
            "mistral": "Mistral",
            "tensorflow": "TensorFlow",
            "pytorch": "PyTorch",
            "hugging face": "Hugging Face",
            "agi": "AGI",
            "ai safety": "AI Safety",
            "machine learning": "Machine Learning",
            "deep learning": "Deep Learning",
            "neural network": "Neural Network",
            "robotics": "Robotics",
            "code generation": "Code Generation",
            "text-to-image": "Text-to-Image",
            "text-to-video": "Text-to-Video",
        }

        for keyword, tag in tag_mapping.items():
            if keyword in title_lower and tag not in tags:
                tags.append(tag)

        # 如果没有匹配到具体标签，添加通用 AI 标签
        if not tags:
            tags.append("AI")

        return tags
