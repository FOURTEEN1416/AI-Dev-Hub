"""
机会（Opportunity）业务逻辑层
处理机会相关的所有业务逻辑，包括查询、创建、搜索等
"""

from typing import Any, Optional

from sqlalchemy import Select, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.opportunity import Opportunity
from app.schemas.opportunity import (
    OpportunityAdvancedFilter,
    OpportunityCreate,
    OpportunityListResponse,
    OpportunityResponse,
)


class OpportunityService:
    """机会业务逻辑服务类"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_opportunities(
        self,
        filters: dict[str, Any],
        page: int = 1,
        limit: int = 20,
    ) -> OpportunityListResponse:
        """
        获取机会列表（支持多条件筛选和分页）

        Args:
            filters: 筛选条件字典，包含 type, source, status, tags, keyword
            page: 页码，从 1 开始
            limit: 每页数量

        Returns:
            分页后的机会列表响应
        """
        # 构建基础查询
        query: Select = select(Opportunity).where(Opportunity.status != "deleted")
        count_query: Select = select(func.count()).select_from(Opportunity).where(
            Opportunity.status != "deleted"
        )

        # 按类型筛选
        if filters.get("type"):
            query = query.where(Opportunity.type == filters["type"])
            count_query = count_query.where(Opportunity.type == filters["type"])

        # 按来源筛选
        if filters.get("source"):
            query = query.where(Opportunity.source == filters["source"])
            count_query = count_query.where(Opportunity.source == filters["source"])

        # 按状态筛选
        if filters.get("status"):
            query = query.where(Opportunity.status == filters["status"])
            count_query = count_query.where(Opportunity.status == filters["status"])

        # 按标签筛选（JSON 数组包含查询）
        if filters.get("tags"):
            for tag in filters["tags"]:
                # 使用 JSON 函数检查标签是否存在于数组中
                # SQLite/PostgreSQL 兼容的 JSON 查询
                tag_condition = func.json_extract(Opportunity.tags, '$').contains(tag)
                query = query.where(tag_condition)
                count_query = count_query.where(tag_condition)

        # 关键词模糊搜索
        if filters.get("keyword"):
            keyword = f"%{filters['keyword']}%"
            keyword_condition = or_(
                Opportunity.title.ilike(keyword),
                Opportunity.description.ilike(keyword),
                Opportunity.source.ilike(keyword),
            )
            query = query.where(keyword_condition)
            count_query = count_query.where(keyword_condition)

        # 查询总数
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 分页查询
        offset = (page - 1) * limit
        query = query.order_by(Opportunity.created_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        opportunities = result.scalars().all()

        return OpportunityListResponse(
            items=[OpportunityResponse.model_validate(op) for op in opportunities],
            total=total,
            page=page,
            limit=limit,
        )

    async def get_opportunity(self, opportunity_id: int) -> Optional[OpportunityResponse]:
        """
        根据 ID 获取单条机会记录

        Args:
            opportunity_id: 机会ID

        Returns:
            机会响应模式，不存在时返回 None
        """
        query = select(Opportunity).where(Opportunity.id == opportunity_id)
        result = await self.db.execute(query)
        opportunity = result.scalar_one_or_none()

        if opportunity is None:
            return None

        return OpportunityResponse.model_validate(opportunity)

    async def create_opportunity(self, data: OpportunityCreate) -> OpportunityResponse:
        """
        创建新的机会记录

        Args:
            data: 创建机会的数据模式

        Returns:
            新创建的机会响应模式
        """
        opportunity = Opportunity(**data.model_dump())
        self.db.add(opportunity)
        await self.db.flush()
        await self.db.refresh(opportunity)

        return OpportunityResponse.model_validate(opportunity)

    async def search_opportunities(
        self,
        keyword: str,
        page: int = 1,
        limit: int = 20,
    ) -> OpportunityListResponse:
        """
        全文搜索机会

        Args:
            keyword: 搜索关键词
            page: 页码，从 1 开始
            limit: 每页数量

        Returns:
            分页后的搜索结果
        """
        search_pattern = f"%{keyword}%"
        search_condition = or_(
            Opportunity.title.ilike(search_pattern),
            Opportunity.description.ilike(search_pattern),
            Opportunity.reward.ilike(search_pattern),
            Opportunity.requirements.ilike(search_pattern),
        )

        # 构建查询
        query = (
            select(Opportunity)
            .where(search_condition)
            .where(Opportunity.status != "deleted")
        )
        count_query = (
            select(func.count())
            .select_from(Opportunity)
            .where(search_condition)
            .where(Opportunity.status != "deleted")
        )

        # 查询总数
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 分页查询
        offset = (page - 1) * limit
        query = query.order_by(Opportunity.created_at.desc()).offset(offset).limit(limit)

        result = await self.db.execute(query)
        opportunities = result.scalars().all()

        return OpportunityListResponse(
            items=[OpportunityResponse.model_validate(op) for op in opportunities],
            total=total,
            page=page,
            limit=limit,
        )

    async def get_distinct_types(self) -> list[str]:
        """
        获取所有不重复的机会类型

        Returns:
            类型字符串列表
        """
        query = select(Opportunity.type).distinct().where(Opportunity.status != "deleted")
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_distinct_sources(self) -> list[str]:
        """
        获取所有不重复的来源平台

        Returns:
            来源字符串列表
        """
        query = select(Opportunity.source).distinct().where(Opportunity.status != "deleted")
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def search_opportunities_fulltext(
        self,
        keyword: str,
        filters: Optional[OpportunityAdvancedFilter] = None,
        page: int = 1,
        limit: int = 20,
    ) -> OpportunityListResponse:
        """
        全文搜索

        使用 LIKE 模糊匹配实现搜索（兼容 SQLite 和 PostgreSQL）

        Args:
            keyword: 搜索关键词
            filters: 高级筛选条件
            page: 页码，从 1 开始
            limit: 每页数量

        Returns:
            分页后的搜索结果
        """
        # 构建搜索条件（使用 LIKE 模糊匹配，兼容 SQLite 和 PostgreSQL）
        search_pattern = f"%{keyword}%"
        search_condition = or_(
            Opportunity.title.ilike(search_pattern),
            Opportunity.description.ilike(search_pattern),
            Opportunity.source.ilike(search_pattern),
        )

        # 基础查询
        query = select(Opportunity).where(
            search_condition
        ).where(Opportunity.status != "deleted")

        count_query = select(func.count()).select_from(Opportunity).where(
            search_condition
        ).where(Opportunity.status != "deleted")

        # 应用高级筛选
        if filters:
            query, count_query = self._apply_advanced_filters(query, count_query, filters)

        # 查询总数
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 排序和分页
        offset = (page - 1) * limit
        if filters:
            query = self._apply_sorting(query, filters.sort_by, filters.sort_order)
        else:
            query = query.order_by(Opportunity.created_at.desc())
        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        opportunities = result.scalars().all()

        return OpportunityListResponse(
            items=[OpportunityResponse.model_validate(op) for op in opportunities],
            total=total,
            page=page,
            limit=limit,
        )

    async def get_opportunities_advanced(
        self,
        filters: OpportunityAdvancedFilter,
        page: int = 1,
        limit: int = 20,
    ) -> OpportunityListResponse:
        """
        高级筛选

        支持多选类型、来源、标签
        支持时间范围筛选
        支持多种排序方式

        Args:
            filters: 高级筛选条件
            page: 页码，从 1 开始
            limit: 每页数量

        Returns:
            分页后的机会列表响应
        """
        # 构建基础查询
        query: Select = select(Opportunity).where(Opportunity.status != "deleted")
        count_query: Select = select(func.count()).select_from(Opportunity).where(
            Opportunity.status != "deleted"
        )

        # 应用高级筛选
        query, count_query = self._apply_advanced_filters(query, count_query, filters)

        # 查询总数
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 排序和分页
        offset = (page - 1) * limit
        query = self._apply_sorting(query, filters.sort_by, filters.sort_order)
        query = query.offset(offset).limit(limit)

        result = await self.db.execute(query)
        opportunities = result.scalars().all()

        return OpportunityListResponse(
            items=[OpportunityResponse.model_validate(op) for op in opportunities],
            total=total,
            page=page,
            limit=limit,
        )

    def _apply_advanced_filters(
        self,
        query: Select,
        count_query: Select,
        filters: OpportunityAdvancedFilter,
    ) -> tuple[Select, Select]:
        """
        应用高级筛选条件到查询

        Args:
            query: 主查询
            count_query: 计数查询
            filters: 筛选条件

        Returns:
            应用筛选后的查询元组
        """
        # 关键词搜索
        if filters.keyword:
            keyword = f"%{filters.keyword}%"
            keyword_condition = or_(
                Opportunity.title.ilike(keyword),
                Opportunity.description.ilike(keyword),
            )
            query = query.where(keyword_condition)
            count_query = count_query.where(keyword_condition)

        # 多选类型筛选
        if filters.types:
            query = query.where(Opportunity.type.in_(filters.types))
            count_query = count_query.where(Opportunity.type.in_(filters.types))

        # 多选来源筛选
        if filters.sources:
            query = query.where(Opportunity.source.in_(filters.sources))
            count_query = count_query.where(Opportunity.source.in_(filters.sources))

        # 多选标签筛选
        if filters.tags:
            for tag in filters.tags:
                tag_condition = func.json_extract(Opportunity.tags, '$').contains(tag)
                query = query.where(tag_condition)
                count_query = count_query.where(tag_condition)

        # 状态筛选
        if filters.status:
            query = query.where(Opportunity.status == filters.status)
            count_query = count_query.where(Opportunity.status == filters.status)

        # 是否有截止日期
        if filters.has_deadline is not None:
            if filters.has_deadline:
                query = query.where(Opportunity.deadline.isnot(None))
                count_query = count_query.where(Opportunity.deadline.isnot(None))
            else:
                query = query.where(Opportunity.deadline.is_(None))
                count_query = count_query.where(Opportunity.deadline.is_(None))

        # 截止日期范围
        if filters.deadline_start:
            query = query.where(Opportunity.deadline >= filters.deadline_start)
            count_query = count_query.where(Opportunity.deadline >= filters.deadline_start)
        if filters.deadline_end:
            query = query.where(Opportunity.deadline <= filters.deadline_end)
            count_query = count_query.where(Opportunity.deadline <= filters.deadline_end)

        # 创建时间范围
        if filters.created_start:
            query = query.where(Opportunity.created_at >= filters.created_start)
            count_query = count_query.where(Opportunity.created_at >= filters.created_start)
        if filters.created_end:
            query = query.where(Opportunity.created_at <= filters.created_end)
            count_query = count_query.where(Opportunity.created_at <= filters.created_end)

        return query, count_query

    def _apply_sorting(self, query: Select, sort_by: str, sort_order: str) -> Select:
        """
        应用排序到查询

        Args:
            query: 查询对象
            sort_by: 排序字段
            sort_order: 排序方向

        Returns:
            应用排序后的查询
        """
        # 确定排序字段
        sort_column = Opportunity.created_at
        if sort_by == "deadline":
            sort_column = Opportunity.deadline
        elif sort_by == "title":
            sort_column = Opportunity.title

        # 确定排序方向
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc().nulls_last())
        else:
            query = query.order_by(sort_column.desc().nulls_last())

        return query

    async def get_popular_tags(self, limit: int = 20) -> list[str]:
        """
        获取热门标签

        统计 tags 数组中出现频率最高的标签

        Args:
            limit: 返回数量限制

        Returns:
            热门标签列表
        """
        # 获取所有标签并统计频率（兼容 SQLite 和 PostgreSQL）
        query = select(Opportunity.tags).where(
            Opportunity.status != "deleted",
            Opportunity.tags.isnot(None)
        )
        result = await self.db.execute(query)
        
        # 在 Python 中统计标签频率
        tag_counts: dict[str, int] = {}
        for row in result.fetchall():
            tags = row[0]
            if tags:
                for tag in tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 按频率排序并返回
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, _ in sorted_tags[:limit]]

    async def get_recent_sources(self, limit: int = 10) -> list[str]:
        """
        获取最近活跃的来源

        Args:
            limit: 返回数量限制

        Returns:
            最近活跃的来源列表
        """
        # 按创建时间倒序获取最近的来源
        query = (
            select(Opportunity.source)
            .where(Opportunity.status != "deleted")
            .distinct(Opportunity.source)
            .order_by(Opportunity.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_filter_options(self) -> dict[str, list[str]]:
        """
        获取所有筛选选项（类型、来源、标签）

        Returns:
            包含所有筛选选项的字典
        """
        types = await self.get_distinct_types()
        sources = await self.get_distinct_sources()
        tags = await self.get_popular_tags(limit=50)

        return {
            "types": types,
            "sources": sources,
            "tags": tags,
        }
