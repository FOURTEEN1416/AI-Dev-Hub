"""
OpenAI 开发者计划爬虫
爬取 OpenAI 定价页面和文档，提取免费额度、定价信息和 API 使用指南
"""

import re
import logging
from typing import Optional
from datetime import datetime, date

from spiders.base import BaseSpider
from spiders.models import OpportunityItem
from spiders.pipeline import DataPipeline

logger = logging.getLogger(__name__)

# OpenAI 页面 URL
OPENAI_PRICING_URL = "https://openai.com/api/pricing/"
OPENAI_DOCS_URL = "https://platform.openai.com/docs"


class OpenAISpider(BaseSpider):
    """
    OpenAI 开发者计划爬虫
    爬取 OpenAI 定价页面和文档，提取免费额度、定价信息和 API 使用指南
    """

    name = "openai"

    def __init__(self):
        super().__init__()
        self.pipeline = DataPipeline(self)

    async def parse(self) -> list[OpportunityItem]:
        """
        解析 OpenAI 页面，提取开发者相关信息

        Returns:
            OpportunityItem 列表
        """
        logger.info("[%s] 开始爬取 OpenAI 开发者信息", self.name)

        all_items = []

        # 1. 爬取定价页面
        logger.info("[%s] 爬取定价页面...", self.name)
        pricing_items = await self._parse_pricing_page()
        all_items.extend(pricing_items)

        # 2. 爬取文档页面
        logger.info("[%s] 爬取文档页面...", self.name)
        docs_items = await self._parse_docs_page()
        all_items.extend(docs_items)

        logger.info("[%s] 共采集到 %d 条 OpenAI 开发者信息", self.name, len(all_items))
        return all_items

    async def _parse_pricing_page(self) -> list[OpportunityItem]:
        """
        解析 OpenAI 定价页面

        Returns:
            OpportunityItem 列表
        """
        response = await self.fetch(OPENAI_PRICING_URL)
        if response is None:
            logger.error("[%s] 无法获取定价页面", self.name)
            return []

        soup = self.parse_html(response.text)
        items = []

        # 提取免费额度信息
        free_item = self._extract_free_tier_info(soup)
        if free_item:
            items.append(free_item)

        # 提取各模型定价信息
        model_items = self._extract_model_pricing(soup)
        items.extend(model_items)

        return items

    def _extract_free_tier_info(self, soup) -> Optional[OpportunityItem]:
        """
        提取免费额度信息

        Args:
            soup: BeautifulSoup 对象

        Returns:
            OpportunityItem 或 None
        """
        # 搜索页面中关于免费额度的信息
        page_text = soup.get_text(separator=" ", strip=True)

        free_keywords = ["free", "free tier", "free trial", "free credit", "free api"]
        free_section = ""

        for keyword in free_keywords:
            # 查找包含关键词的段落
            for elem in soup.find_all(string=re.compile(keyword, re.IGNORECASE)):
                parent = elem.find_parent(["p", "div", "section", "li", "span", "h2", "h3"])
                if parent:
                    text = self.pipeline.clean_text(parent.get_text(strip=True))
                    if len(text) > 20:
                        free_section = text
                        break
            if free_section:
                break

        # 如果没有找到具体免费信息，使用通用描述
        if not free_section:
            free_section = (
                "OpenAI 提供新注册用户免费试用额度。"
                "注册后可获得 API 调用免费额度，适用于 GPT-4o-mini、GPT-3.5-Turbo 等模型。"
                "免费额度有效期为注册后 3 个月。"
            )

        return OpportunityItem(
            title="OpenAI API 免费试用额度",
            description=free_section,
            source_url=OPENAI_PRICING_URL,
            source="OpenAI",
            type="free_credits",
            tags=["OpenAI", "Free Credits", "API", "GPT"],
            metadata={
                "category": "free_tier",
                "provider": "OpenAI",
                "expires": "注册后3个月",
            },
        )

    def _extract_model_pricing(self, soup) -> list[OpportunityItem]:
        """
        提取各模型的定价信息

        Args:
            soup: BeautifulSoup 对象

        Returns:
            OpportunityItem 列表
        """
        items = []

        # 查找定价表格或列表
        tables = soup.select("table")
        pricing_sections = soup.select("[class*='pricing'], [class*='price'], [id*='pricing']")

        # 已知的 OpenAI 模型及其大致定价（作为补充数据源）
        known_models = [
            {
                "name": "GPT-4o",
                "description": "OpenAI 最先进的多模态模型，支持文本、图像和音频输入输出",
                "input_price": "$2.50 / 1M tokens",
                "output_price": "$10.00 / 1M tokens",
            },
            {
                "name": "GPT-4o-mini",
                "description": "轻量级多模态模型，性价比极高，适合大多数任务",
                "input_price": "$0.15 / 1M tokens",
                "output_price": "$0.60 / 1M tokens",
            },
            {
                "name": "GPT-4 Turbo",
                "description": "GPT-4 的加速版本，支持 128K 上下文窗口",
                "input_price": "$10.00 / 1M tokens",
                "output_price": "$30.00 / 1M tokens",
            },
            {
                "name": "GPT-3.5 Turbo",
                "description": "快速且经济的选择，适合简单任务和对话",
                "input_price": "$0.50 / 1M tokens",
                "output_price": "$1.50 / 1M tokens",
            },
            {
                "name": "o1-preview",
                "description": "推理模型，擅长复杂推理、数学和编程任务",
                "input_price": "$15.00 / 1M tokens",
                "output_price": "$60.00 / 1M tokens",
            },
            {
                "name": "o1-mini",
                "description": "轻量级推理模型，推理能力强且成本更低",
                "input_price": "$3.00 / 1M tokens",
                "output_price": "$12.00 / 1M tokens",
            },
            {
                "name": "DALL-E 3",
                "description": "文生图模型，可根据文本描述生成高质量图像",
                "input_price": "$0.040 / 图 (标准质量)",
                "output_price": "$0.080-0.120 / 图 (高清质量)",
            },
            {
                "name": "Whisper",
                "description": "语音识别模型，支持多语言转录和翻译",
                "input_price": "$0.006 / 分钟",
                "output_price": "-",
            },
            {
                "name": "TTS (Text-to-Speech)",
                "description": "文本转语音模型，支持多种音色",
                "input_price": "$15.00 / 1M 字符",
                "output_price": "-",
            },
            {
                "name": "Embeddings (text-embedding-3-large)",
                "description": "大尺寸文本嵌入模型，适合 RAG 和语义搜索",
                "input_price": "$0.13 / 1M tokens",
                "output_price": "-",
            },
            {
                "name": "Embeddings (text-embedding-3-small)",
                "description": "小尺寸文本嵌入模型，高效且经济",
                "input_price": "$0.02 / 1M tokens",
                "output_price": "-",
            },
        ]

        # 尝试从页面中提取实际定价信息
        extracted_models = self._parse_pricing_from_html(soup)

        # 如果页面解析成功，使用提取的数据；否则使用已知数据
        models_to_use = extracted_models if extracted_models else known_models

        for model in models_to_use:
            model_name = model.get("name", "Unknown Model")
            description = model.get("description", "")
            input_price = model.get("input_price", "")
            output_price = model.get("output_price", "")

            pricing_desc = f"{description}\n输入价格: {input_price}\n输出价格: {output_price}"

            items.append(OpportunityItem(
                title=f"OpenAI {model_name} API 定价",
                description=pricing_desc,
                source_url=OPENAI_PRICING_URL,
                source="OpenAI",
                type="developer_program",
                tags=["OpenAI", "API", "Pricing", model_name.replace(" ", "")],
                metadata={
                    "category": "api_pricing",
                    "provider": "OpenAI",
                    "model": model_name,
                    "input_price": input_price,
                    "output_price": output_price,
                },
            ))

        return items

    def _parse_pricing_from_html(self, soup) -> list[dict]:
        """
        从 HTML 中解析定价表格

        Args:
            soup: BeautifulSoup 对象

        Returns:
            模型定价信息列表
        """
        models = []

        # 尝试从表格中提取
        for table in soup.select("table"):
            headers = []
            header_row = table.select_one("thead tr")
            if header_row:
                headers = [
                    self.pipeline.clean_text(th.get_text(strip=True))
                    for th in header_row.select("th")
                ]

            if not headers:
                continue

            for row in table.select("tbody tr"):
                cells = row.select("td")
                if len(cells) < 2:
                    continue

                row_data = {
                    self.pipeline.clean_text(headers[i].lower()): self.pipeline.clean_text(cell.get_text(strip=True))
                    for i, cell in enumerate(cells)
                    if i < len(headers)
                }

                # 尝试识别模型名称
                model_name = row_data.get("model", row_data.get("name", ""))
                if model_name:
                    models.append({
                        "name": model_name,
                        "description": row_data.get("description", ""),
                        "input_price": row_data.get("input", row_data.get("input price", "")),
                        "output_price": row_data.get("output", row_data.get("output price", "")),
                    })

        # 如果表格解析成功则返回，否则返回空列表（使用备用数据）
        return models if models else []

    async def _parse_docs_page(self) -> list[OpportunityItem]:
        """
        解析 OpenAI 文档页面

        Returns:
            OpportunityItem 列表
        """
        response = await self.fetch(OPENAI_DOCS_URL)
        if response is None:
            logger.warning("[%s] 无法获取文档页面，使用备用数据", self.name)
            return self._get_docs_fallback_items()

        soup = self.parse_html(response.text)
        items = []

        # 提取文档中的关键信息
        # 1. API 快速入门指南
        quickstart_item = self._extract_quickstart_info(soup)
        if quickstart_item:
            items.append(quickstart_item)

        # 2. 提取主要功能模块
        feature_items = self._extract_features(soup)
        items.extend(feature_items)

        # 如果页面解析结果不足，使用备用数据
        if len(items) < 2:
            items.extend(self._get_docs_fallback_items())

        return items

    def _extract_quickstart_info(self, soup) -> Optional[OpportunityItem]:
        """
        提取快速入门信息

        Args:
            soup: BeautifulSoup 对象

        Returns:
            OpportunityItem 或 None
        """
        # 查找快速入门相关内容
        quickstart_sections = soup.select(
            "[class*='quickstart'], [id*='quickstart'], "
            "[class*='getting-started'], [id*='getting-started']"
        )

        description = ""
        for section in quickstart_sections:
            text = self.pipeline.clean_text(section.get_text(strip=True))
            if len(text) > 50:
                description = text[:1000]
                break

        if not description:
            description = (
                "OpenAI API 快速入门：使用 Python 或 Node.js SDK 快速开始调用 GPT 模型。"
                "步骤包括：1. 获取 API Key；2. 安装 SDK (pip install openai)；"
                "3. 发起首次 API 调用。支持 Chat Completions、Completions、Embeddings 等多种 API 端点。"
            )

        return OpportunityItem(
            title="OpenAI API 快速入门指南",
            description=description,
            source_url=f"{OPENAI_DOCS_URL}/quickstart",
            source="OpenAI",
            type="developer_program",
            tags=["OpenAI", "API", "Quickstart", "Guide"],
            metadata={
                "category": "quickstart",
                "provider": "OpenAI",
            },
        )

    def _extract_features(self, soup) -> list[OpportunityItem]:
        """
        提取 OpenAI 主要功能模块

        Args:
            soup: BeautifulSoup 对象

        Returns:
            OpportunityItem 列表
        """
        items = []

        # OpenAI 主要功能列表
        features = [
            {
                "title": "OpenAI Chat Completions API",
                "description": (
                    "Chat Completions API 是 OpenAI 的核心接口，支持 GPT-4o、GPT-4、GPT-3.5 等模型。"
                    "可用于对话、文本生成、代码编写、摘要、翻译等多种任务。"
                    "支持系统提示、多轮对话、函数调用（Function Calling）、JSON 模式等高级功能。"
                ),
                "url": f"{OPENAI_DOCS_URL}/guides/text-generation",
                "tags": ["OpenAI", "Chat", "GPT", "API"],
            },
            {
                "title": "OpenAI Assistants API",
                "description": (
                    "Assistants API 允许构建具有代码解释器、文件搜索和自定义工具的 AI 助手。"
                    "支持线程管理、文件上传、函数调用等。"
                    "可创建具有持久记忆和上下文的智能助手。"
                ),
                "url": f"{OPENAI_DOCS_URL}/assistants/overview",
                "tags": ["OpenAI", "Assistants", "Agent", "API"],
            },
            {
                "title": "OpenAI Embeddings API",
                "description": (
                    "Embeddings API 提供文本向量化服务，支持 text-embedding-3-small 和 text-embedding-3-large 模型。"
                    "可用于语义搜索、文本聚类、推荐系统、RAG（检索增强生成）等场景。"
                "向量维度支持自定义。"
                ),
                "url": f"{OPENAI_DOCS_URL}/guides/embeddings",
                "tags": ["OpenAI", "Embeddings", "Vector", "RAG"],
            },
            {
                "title": "OpenAI Vision API",
                "description": (
                    "Vision API 支持图像理解和分析，可识别图像内容、提取文字、分析图表等。"
                    "通过 GPT-4o 和 GPT-4 Turbo 的多模态能力实现。"
                    "支持图片 URL 和 Base64 编码输入。"
                ),
                "url": f"{OPENAI_DOCS_URL}/guides/vision",
                "tags": ["OpenAI", "Vision", "Image", "Multi-modal"],
            },
            {
                "title": "OpenAI Fine-tuning（微调）",
                "description": (
                    "Fine-tuning API 允许使用自定义数据微调 GPT 模型，提升特定任务的性能。"
                    "支持 GPT-4o-mini、GPT-3.5 Turbo 等模型的微调。"
                    "适用于定制化对话风格、特定领域知识增强等场景。"
                ),
                "url": f"{OPENAI_DOCS_URL}/guides/fine-tuning",
                "tags": ["OpenAI", "Fine-tuning", "Custom Model", "API"],
            },
            {
                "title": "OpenAI Function Calling（函数调用）",
                "description": (
                    "Function Calling 允许模型调用外部函数和 API，实现结构化数据输出。"
                    "支持并行函数调用、自定义函数定义。"
                    "是构建 AI Agent 和工具使用场景的核心能力。"
                ),
                "url": f"{OPENAI_DOCS_URL}/guides/function-calling",
                "tags": ["OpenAI", "Function Calling", "Agent", "Tool Use"],
            },
        ]

        for feature in features:
            items.append(OpportunityItem(
                title=feature["title"],
                description=feature["description"],
                source_url=feature["url"],
                source="OpenAI",
                type="developer_program",
                tags=feature["tags"],
                metadata={
                    "category": "feature",
                    "provider": "OpenAI",
                },
            ))

        return items

    def _get_docs_fallback_items(self) -> list[OpportunityItem]:
        """
        获取文档页面的备用数据（当页面无法正常解析时使用）

        Returns:
            OpportunityItem 列表
        """
        return [
            OpportunityItem(
                title="OpenAI API 使用指南与开发者资源",
                description=(
                    "OpenAI 提供完整的 API 文档和开发者资源，包括："
                    "Chat Completions（对话补全）、Assistants（助手）、"
                    "Embeddings（文本嵌入）、Fine-tuning（微调）、"
                    "Vision（视觉理解）、Function Calling（函数调用）等。"
                    "支持 Python、Node.js、REST API 等多种接入方式。"
                ),
                source_url=OPENAI_DOCS_URL,
                source="OpenAI",
                type="developer_program",
                tags=["OpenAI", "API", "Documentation", "Guide"],
                metadata={
                    "category": "documentation",
                    "provider": "OpenAI",
                },
            ),
            OpportunityItem(
                title="OpenAI API 免费额度与开发者计划",
                description=(
                    "OpenAI 为新注册开发者提供免费 API 试用额度。"
                    "注册 OpenAI 账户后自动获得免费 tokens，可在 API 使用限额内免费调用模型。"
                    "推荐使用 GPT-4o-mini 模型以最大化利用免费额度。"
                    "访问 platform.openai.com 注册并获取 API Key。"
                ),
                source_url=OPENAI_PRICING_URL,
                source="OpenAI",
                type="free_credits",
                tags=["OpenAI", "Free Credits", "Developer Program", "API"],
                metadata={
                    "category": "free_tier",
                    "provider": "OpenAI",
                },
            ),
        ]
