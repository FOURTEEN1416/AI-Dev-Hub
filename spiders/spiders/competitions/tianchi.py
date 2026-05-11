"""
阿里天池比赛爬虫
爬取阿里天池比赛平台，提取 AI 相关比赛信息
"""

import re
import logging
from typing import Optional
from datetime import datetime

from spiders.base import BaseSpider
from spiders.models import OpportunityItem
from spiders.pipeline import DataPipeline

logger = logging.getLogger(__name__)

# 天池比赛平台 URL
TIANCHI_COMPETITIONS_URL = "https://tianchi.aliyun.com/competition"

# AI 相关标签关键词
AI_COMPETITION_KEYWORDS = [
    "ai", "ml", "machine learning", "deep learning",
    "nlp", "computer vision", "image", "text",
    "classification", "regression", "detection",
    "segmentation", "generation", "recommendation",
    "forecasting", "neural", "transformer", "bert", "gpt",
    "llm", "language model", "speech", "audio",
    "video", "time series", "anomaly detection",
    "人工智能", "机器学习", "深度学习", "自然语言处理",
    "计算机视觉", "图像识别", "文本分类", "推荐系统",
    "知识图谱", "大模型", "语音识别",
]


class TianchiSpider(BaseSpider):
    """
    阿里天池比赛爬虫

    目标URL: https://tianchi.aliyun.com/competition
    数据类型: competition
    来源: 天池

    解析内容:
    - 比赛名称
    - 比赛描述
    - 截止日期
    - 奖金/奖励
    - 比赛状态（进行中/已结束/即将开始）
    - 标签（AI、大数据、算法等）

    注意事项:
    - 天池页面可能是动态渲染，需要使用 Playwright
    - 处理分页
    - 过滤 AI 相关比赛
    """

    name = "tianchi"

    def __init__(self):
        super().__init__()
        self.pipeline = DataPipeline(self)

    async def parse(self) -> list[OpportunityItem]:
        """
        解析天池比赛页面

        Returns:
            OpportunityItem 列表
        """
        logger.info("[%s] 开始爬取天池比赛页面", self.name)

        all_items = []

        # 尝试使用 Playwright 渲染动态页面
        try:
            items = await self._parse_with_playwright()
            all_items.extend(items)
        except Exception as e:
            logger.warning("[%s] Playwright 渲染失败，尝试直接请求: %s", self.name, str(e))
            # 回退到直接请求
            items = await self._parse_directly()
            all_items.extend(items)

        logger.info("[%s] 共采集到 %d 个比赛", self.name, len(all_items))
        return all_items

    async def _parse_with_playwright(self) -> list[OpportunityItem]:
        """
        使用 Playwright 渲染并解析页面

        Returns:
            OpportunityItem 列表
        """
        from playwright.async_api import async_playwright

        items = []

        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=self._get_random_ua(),
            )
            page = await context.new_page()

            try:
                # 访问比赛列表页
                logger.info("[%s] Playwright 正在加载页面: %s", self.name, TIANCHI_COMPETITIONS_URL)
                await page.goto(TIANCHI_COMPETITIONS_URL, wait_until="networkidle", timeout=30000)

                # 等待比赛列表加载
                await page.wait_for_selector(".competition-item, .comp-item, [class*='competition']", timeout=15000)

                # 获取页面内容
                content = await page.content()
                soup = self.parse_html(content)

                # 解析比赛列表
                items = self._parse_competition_list(soup)

                # 尝试翻页
                for page_num in range(2, 4):  # 最多爬取3页
                    try:
                        # 查找下一页按钮
                        next_btn = await page.query_selector(".next, .pagination-next, [class*='next']")
                        if next_btn:
                            await next_btn.click()
                            await page.wait_for_timeout(2000)  # 等待加载
                            content = await page.content()
                            soup = self.parse_html(content)
                            page_items = self._parse_competition_list(soup)
                            items.extend(page_items)
                            await self._random_delay()
                        else:
                            break
                    except Exception as e:
                        logger.debug("[%s] 翻页失败: %s", self.name, str(e))
                        break

            except Exception as e:
                logger.error("[%s] Playwright 解析失败: %s", self.name, str(e))
            finally:
                await browser.close()

        return items

    async def _parse_directly(self) -> list[OpportunityItem]:
        """
        直接请求页面解析（作为 Playwright 的回退方案）

        Returns:
            OpportunityItem 列表
        """
        response = await self.fetch(TIANCHI_COMPETITIONS_URL)
        if response is None:
            logger.error("[%s] 无法获取比赛页面", self.name)
            return []

        soup = self.parse_html(response.text)
        return self._parse_competition_list(soup)

    def _parse_competition_list(self, soup) -> list[OpportunityItem]:
        """
        解析比赛列表

        Args:
            soup: BeautifulSoup 对象

        Returns:
            OpportunityItem 列表
        """
        items = []

        # 尝试多种选择器
        competition_elements = (
            soup.select(".competition-item") or
            soup.select(".comp-item") or
            soup.select("[class*='competition-card']") or
            soup.select("a[href*='/competition/']")
        )

        if not competition_elements:
            logger.warning("[%s] 未找到比赛条目", self.name)
            return items

        logger.info("[%s] 找到 %d 个比赛元素", self.name, len(competition_elements))

        for element in competition_elements:
            try:
                item = self._parse_competition_element(element)
                if item is not None:
                    items.append(item)
            except Exception as e:
                logger.error("[%s] 解析比赛条目失败: %s", self.name, str(e))
                self.error_count += 1

        return items

    def _parse_competition_element(self, element) -> Optional[OpportunityItem]:
        """
        解析单个比赛元素

        Args:
            element: BeautifulSoup 元素

        Returns:
            OpportunityItem 或 None
        """
        # 提取标题
        title_elem = (
            element.select_one(".title") or
            element.select_one("h3") or
            element.select_one("h4") or
            element.select_one("a")
        )

        if not title_elem:
            return None

        title = self.pipeline.clean_text(title_elem.get_text(strip=True))

        if not title:
            return None

        # 提取链接
        link_elem = element if element.name == "a" else element.select_one("a")
        href = link_elem.get("href", "") if link_elem else ""

        if href:
            if href.startswith("/"):
                source_url = f"https://tianchi.aliyun.com{href}"
            elif href.startswith("http"):
                source_url = href
            else:
                source_url = f"https://tianchi.aliyun.com/competition/{href}"
        else:
            # 没有链接则跳过
            return None

        # 提取描述
        description = ""
        desc_elem = (
            element.select_one(".desc") or
            element.select_one(".description") or
            element.select_one("p")
        )
        if desc_elem:
            description = self.pipeline.clean_text(desc_elem.get_text(strip=True))

        # 提取截止日期
        deadline = None
        deadline_elem = (
            element.select_one(".deadline") or
            element.select_one(".date") or
            element.select_one("time")
        )
        if deadline_elem:
            deadline_text = self.pipeline.clean_text(deadline_elem.get_text(strip=True))
            deadline = self._parse_deadline(deadline_text)

        # 提取奖励
        reward = None
        reward_elem = (
            element.select_one(".reward") or
            element.select_one(".prize") or
            element.select_one("[class*='bonus']")
        )
        if reward_elem:
            reward = self.pipeline.clean_text(reward_elem.get_text(strip=True))
        else:
            # 尝试从文本中提取奖励信息
            full_text = element.get_text()
            reward_match = re.search(r"奖金[：:]\s*([\d,]+万?元?)", full_text)
            if reward_match:
                reward = reward_match.group(1)
            else:
                reward_match = re.search(r"¥[\d,]+万?", full_text)
                if reward_match:
                    reward = reward_match.group(0)

        # 提取比赛状态
        status = "进行中"
        status_elem = (
            element.select_one(".status") or
            element.select_one(".state") or
            element.select_one("[class*='status']")
        )
        if status_elem:
            status_text = self.pipeline.clean_text(status_elem.get_text(strip=True)).lower()
            if "结束" in status_text or "ended" in status_text:
                status = "已结束"
            elif "即将" in status_text or "coming" in status_text:
                status = "即将开始"

        # 提取标签
        tags = ["天池", "Competition"]
        tag_elems = element.select(".tag, .label, [class*='tag']")
        for tag_elem in tag_elems:
            tag_text = self.pipeline.clean_text(tag_elem.get_text(strip=True))
            if tag_text:
                tags.append(tag_text)

        # 检查是否为 AI 相关比赛
        combined_text = f"{title} {description}".lower()
        is_ai_related = any(kw in combined_text for kw in AI_COMPETITION_KEYWORDS)

        if not is_ai_related:
            self.filtered_count += 1
            return None

        # 补充 AI 相关标签
        for keyword in AI_COMPETITION_KEYWORDS:
            if keyword in combined_text and keyword.title() not in tags:
                tags.append(keyword.title())

        # 提取外部 ID
        external_id = None
        match = re.search(r"/competition/([^/?]+)", source_url)
        if match:
            external_id = match.group(1)

        # 构建元数据
        metadata = {
            "platform": "天池",
            "status": status,
            "category": "competition",
        }

        return OpportunityItem(
            title=title,
            description=description or "阿里天池数据科学竞赛",
            source_url=source_url,
            source="天池",
            type="competition",
            tags=tags,
            external_id=external_id,
            reward=reward,
            deadline=deadline,
            metadata=metadata,
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
            "%Y年%m月%d日",
            "%Y.%m.%d",
            "%Y/%m/%d",
            "%m/%d/%Y",
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(text.strip(), fmt).date()
            except ValueError:
                continue

        # 尝试提取日期数字
        match = re.search(r"(\d{4})[年\-/.](\d{1,2})[月\-/.](\d{1,2})", text)
        if match:
            try:
                return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3))).date()
            except ValueError:
                pass

        return None
