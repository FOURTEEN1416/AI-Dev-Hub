"""
AI 提取适配器模块
用于对爬虫采集的原始内容做 LLM 结构化提取
支持 ScrapeGraphAI 和 LLM API 两种后端
"""

import json
import logging
from typing import Optional

from spiders.config import settings

logger = logging.getLogger(__name__)


# ==================== 抽象基类 ====================


class AIExtractionAdapter:
    """
    AI 提取适配器基类
    子类实现 extract() 方法，将原始文本/HTML 提取为结构化数据
    """

    def __init__(self):
        self._initialized = False

    async def initialize(self):
        """初始化资源（如模型加载、客户端创建）"""
        self._initialized = True

    async def extract(
        self,
        raw_content: str,
        schema: str = "",
        context: Optional[dict] = None,
    ) -> dict:
        """
        对原始内容进行 AI 结构化提取

        Args:
            raw_content: 原始内容（纯文本或清洗后的 HTML）
            schema: 期望提取的字段描述，如 "title, description, tags, difficulty_level"
            context: 可选的上下文信息，如 {"source": "github_trending", "url": "..."}

        Returns:
            提取的结构化数据字典，失败返回空 dict
        """
        raise NotImplementedError

    async def close(self):
        """释放资源"""
        self._initialized = False


# ==================== ScrapeGraphAI 适配器 ====================


class ScrapeGraphAIAdapter(AIExtractionAdapter):
    """
    使用 ScrapeGraphAI 的 SmartScraperGraph 做内容提取

    需要设置 OPENAI_API_KEY 环境变量（或其他 LLM API Key）
    可通过 settings.AI_LLM_MODEL 配置模型
    """

    def __init__(self):
        super().__init__()
        self._graph = None

    async def initialize(self):
        """懒加载 SmartScraperGraph"""
        self._initialized = True
        logger.info("[AI] ScrapeGraphAIAdapter 就绪")

    async def extract(
        self,
        raw_content: str,
        schema: str = "",
        context: Optional[dict] = None,
    ) -> dict:
        if not raw_content or len(raw_content.strip()) < 10:
            return {}

        if not self._initialized:
            await self.initialize()

        try:
            # 动态导入，避免模块级加载失败
            from scrapegraphai.graphs import SmartScraperGraph

            # 构建提取 prompt
            source = (context or {}).get("source", "unknown")
            prompt = f"提取以下信息: {schema}" if schema else "提取内容的标题、描述、标签和关键信息"

            graph_config = {
                "llm": {
                    "model": getattr(settings, "AI_LLM_MODEL", "openai/gpt-4o-mini"),
                    "temperature": 0.1,
                },
                "verbose": getattr(settings, "AI_VERBOSE", False),
            }

            self._graph = SmartScraperGraph(
                prompt=prompt,
                source=raw_content[:8000],  # 限制内容长度
                config=graph_config,
            )

            result = self._graph.run()
            if result and isinstance(result, dict):
                logger.info("[AI] 提取成功: source=%s keys=%s", source, list(result.keys()))
                return result

            logger.warning("[AI] 提取结果为空: source=%s", source)
            return {}

        except ImportError:
            logger.warning("[AI] ScrapeGraphAI 未安装，跳过 AI 提取")
            return {}
        except Exception as e:
            logger.warning("[AI] 提取失败: %s (source=%s)", str(e)[:200], source)
            return {}

    async def close(self):
        self._graph = None
        self._initialized = False


# ==================== 简单 LLM API 适配器（无 ScrapeGraphAI 时使用） ====================


class LLMAPIAdapter(AIExtractionAdapter):
    """
    直接调用 LLM API 做提取（不依赖 ScrapeGraphAI）

    通过 settings.AI_LLM_ENDPOINT 和 settings.AI_LLM_API_KEY 配置
    """

    def __init__(self):
        super().__init__()
        self._client = None

    async def initialize(self):
        self._initialized = True
        logger.info("[AI] LLMAPIAdapter 就绪")

    async def extract(
        self,
        raw_content: str,
        schema: str = "",
        context: Optional[dict] = None,
    ) -> dict:
        if not raw_content or len(raw_content.strip()) < 10:
            return {}

        endpoint = getattr(settings, "AI_LLM_ENDPOINT", "")
        api_key = getattr(settings, "AI_LLM_API_KEY", "")

        if not endpoint:
            logger.debug("[AI] LLMAPIAdapter 未配置 endpoint，跳过")
            return {}

        try:
            import httpx

            prompt = (
                f"从以下内容中提取结构化信息: {schema or '标题、描述、标签和关键数据'}\n"
                f"请用 JSON 格式返回。\n\n内容:\n{raw_content[:6000]}"
            )

            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    endpoint,
                    headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
                    json={
                        "model": getattr(settings, "AI_LLM_MODEL", "gpt-4o-mini"),
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                    },
                )
                resp.raise_for_status()
                data = resp.json()

            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            # 尝试从返回中提取 JSON
            json_match = content.strip()
            if json_match.startswith("```"):
                # 去掉 markdown 代码块标记
                lines = json_match.split("\n")
                lines = [l for l in lines if not l.startswith("```")]
                json_match = "\n".join(lines)

            result = json.loads(json_match)
            if isinstance(result, dict):
                logger.info("[AI] LLM API 提取成功")
                return result
            return {}

        except Exception as e:
            logger.debug("[AI] LLM API 提取失败: %s", str(e)[:200])
            return {}

    async def close(self):
        self._client = None
        self._initialized = False


# ==================== 工厂函数 ====================


def get_ai_adapter() -> Optional[AIExtractionAdapter]:
    """
    获取 AI 提取适配器
    优先使用 ScrapeGraphAI，失败时尝试 LLM API，都不可用则返回 None
    """
    # 先尝试 ScrapeGraphAI
    try:
        import scrapegraphai  # noqa: F401
        logger.debug("[AI] 使用 ScrapeGraphAIAdapter")
        return ScrapeGraphAIAdapter()
    except ImportError:
        pass

    # 再尝试 LLM API
    if getattr(settings, "AI_LLM_ENDPOINT", ""):
        logger.debug("[AI] 使用 LLMAPIAdapter")
        return LLMAPIAdapter()

    logger.debug("[AI] 无可用 AI 适配器")
    return None
