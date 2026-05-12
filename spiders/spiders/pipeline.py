"""
数据管道模块
负责数据清洗、去重检查、数据验证、AI提取和异步入库
"""

import json
import re
import logging
from typing import Optional

from spiders.models import OpportunityItem
from spiders.base import BaseSpider
from spiders.config import settings

# 可选 AI 提取适配器
_AI_AVAILABLE = False
try:
    if settings.ENABLE_AI_EXTRACT:
        from spiders.ai_adapter import AIExtractionAdapter, get_ai_adapter
        _AI_AVAILABLE = True
except ImportError:
    pass
except Exception:
    pass

logger = logging.getLogger(__name__)


class DataPipeline:
    """
    数据管道
    对爬虫采集的原始数据进行清洗、验证和入库
    """

    def __init__(self, spider: BaseSpider):
        """
        初始化数据管道

        Args:
            spider: 爬虫实例，用于调用去重和入库方法
        """
        self.spider = spider

    # ==================== 数据清洗 ====================

    @staticmethod
    def clean_text(text: str) -> str:
        """
        清洗文本：去除多余空白、HTML 标签、特殊字符

        Args:
            text: 原始文本

        Returns:
            清洗后的文本
        """
        if not text:
            return ""

        # 去除 HTML 标签
        text = re.sub(r"<[^>]+>", "", text)

        # 去除 HTML 实体
        html_entities = {
            "&nbsp;": " ",
            "&amp;": "&",
            "&lt;": "<",
            "&gt;": ">",
            "&quot;": '"',
            "&#39;": "'",
            "&apos;": "'",
        }
        for entity, char in html_entities.items():
            text = text.replace(entity, char)

        # 去除多余空白
        text = re.sub(r"\s+", " ", text)

        # 去除首尾空白
        text = text.strip()

        return text

    @staticmethod
    def clean_tags(tags: list[str]) -> list[str]:
        """
        清洗标签列表：去重、去除空白、过滤空标签

        Args:
            tags: 原始标签列表

        Returns:
            清洗后的标签列表
        """
        if not tags:
            return []

        cleaned = []
        seen = set()
        for tag in tags:
            tag = tag.strip()
            if tag and tag.lower() not in seen:
                cleaned.append(tag)
                seen.add(tag.lower())

        return cleaned

    @staticmethod
    def clean_url(url: str) -> str:
        """
        清洗 URL：去除追踪参数、多余空白

        Args:
            url: 原始 URL

        Returns:
            清洗后的 URL
        """
        if not url:
            return ""

        url = url.strip()

        # 去除常见追踪参数
        tracking_params = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "ref"]
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

        parsed = urlparse(url)
        params = parse_qs(parsed.query, keep_blank_values=True)

        # 过滤掉追踪参数
        filtered_params = {
            k: v for k, v in params.items() if k not in tracking_params
        }

        if filtered_params:
            new_query = urlencode(filtered_params, doseq=True)
        else:
            new_query = ""

        cleaned = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        ))

        return cleaned

    @staticmethod
    def parse_star_count(star_str: str) -> Optional[int]:
        """
        解析 Star 数量字符串为整数
        支持格式: "1,234", "1.2k", "1.2M", "1234"

        Args:
            star_str: Star 数量字符串

        Returns:
            整数值，解析失败返回 None
        """
        if not star_str:
            return None

        star_str = star_str.strip().replace(",", "")

        try:
            # 处理 "1.2k" 格式
            if star_str.lower().endswith("k"):
                return int(float(star_str[:-1]) * 1000)
            # 处理 "1.2M" 格式
            elif star_str.lower().endswith("m"):
                return int(float(star_str[:-1]) * 1000000)
            # 处理 "1.2B" 格式
            elif star_str.lower().endswith("b"):
                return int(float(star_str[:-1]) * 1000000000)
            # 普通数字
            else:
                return int(star_str)
        except (ValueError, TypeError):
            return None

    # ==================== 数据验证 ====================

    @staticmethod
    def validate_item(item_data: dict) -> Optional[OpportunityItem]:
        """
        使用 Pydantic 验证并创建 OpportunityItem

        Args:
            item_data: 原始数据字典

        Returns:
            验证通过的 OpportunityItem，验证失败返回 None
        """
        try:
            item = OpportunityItem(**item_data)
            return item
        except Exception as e:
            logger.warning("数据验证失败: %s (错误: %s)", item_data.get("title", "未知"), str(e))
            return None

    # ==================== 完整处理流程 ====================

    async def process_item(self, raw_item: dict) -> Optional[OpportunityItem]:
        """
        处理单条数据：清洗 -> AI 提取 -> 验证 -> 去重

        Args:
            raw_item: 原始数据字典

        Returns:
            处理后的 OpportunityItem，去重或验证失败返回 None
        """
        # 数据清洗
        if "title" in raw_item:
            raw_item["title"] = self.clean_text(raw_item["title"])
        if "description" in raw_item:
            raw_item["description"] = self.clean_text(raw_item["description"])
        if "source_url" in raw_item:
            raw_item["source_url"] = self.clean_url(raw_item["source_url"])
        if "tags" in raw_item:
            raw_item["tags"] = self.clean_tags(raw_item["tags"])

        # AI 提取增强（可选）
        if _AI_AVAILABLE:
            ai_adapter = get_ai_adapter()
            if ai_adapter is not None:
                # 使用清洗后的 description（或 title）作为 AI 提取源
                content = raw_item.get("description") or raw_item.get("title", "")
                if content:
                    ai_result = await ai_adapter.extract(
                        raw_content=content,
                        schema="title, description, tags, difficulty_level, tech_stack",
                        context={"source": getattr(self.spider, "name", "unknown")},
                    )
                    if ai_result:
                        # 仅用 AI 结果填充空字段，不覆盖已有的
                        for key in ("title", "description", "tags"):
                            if key in ai_result and ai_result[key] and not raw_item.get(key):
                                raw_item[key] = ai_result[key]
                        # AI 增强信息存入 metadata（JSON 字段，可扩展）
                        ai_enrichment = {}
                        for key in ("difficulty_level", "tech_stack"):
                            if key in ai_result and ai_result[key]:
                                ai_enrichment[key] = ai_result[key]
                        if ai_enrichment:
                            meta = raw_item.get("metadata") or {}
                            if isinstance(meta, str):
                                try:
                                    meta = json.loads(meta)
                                except (json.JSONDecodeError, TypeError):
                                    meta = {}
                            meta["ai_extracted"] = ai_enrichment
                            raw_item["metadata"] = meta
                    await ai_adapter.close()

        # 数据验证
        item = self.validate_item(raw_item)
        if item is None:
            self.spider.filtered_count += 1
            return None

        # 去重检查
        is_dup = await self.spider.is_duplicate(item.source_url)
        if is_dup:
            self.spider.duplicate_count += 1
            return None

        return item

    async def process_items(self, raw_items: list[dict]) -> list[OpportunityItem]:
        """
        批量处理数据

        Args:
            raw_items: 原始数据字典列表

        Returns:
            处理后的 OpportunityItem 列表
        """
        results = []
        for raw_item in raw_items:
            item = await self.process_item(raw_item)
            if item is not None:
                results.append(item)
        return results

    async def process_and_save(self, raw_items: list[dict]) -> int:
        """
        处理数据并入库

        Args:
            raw_items: 原始数据字典列表

        Returns:
            成功入库的条数
        """
        validated_items = await self.process_items(raw_items)
        if not validated_items:
            return 0

        saved = await self.spider.save_batch_to_db(validated_items)
        self.spider.saved_count += saved
        return saved
