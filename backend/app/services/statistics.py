"""
统计（Statistics）业务逻辑层
处理统计相关的所有业务逻辑，包括概览统计、趋势分析、分布统计等
"""

from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import Date, and_, case, cast, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.opportunity import Opportunity
from app.schemas.statistics import (
    CalendarEvent,
    CalendarOpportunity,
    CalendarResponse,
    DistributionItem,
    DistributionResponse,
    OverviewStats,
    TagCloudItem,
    TagCloudResponse,
    TrendDataPoint,
    TrendDataResponse,
)


class StatisticsService:
    """统计业务逻辑服务类"""

    @staticmethod
    async def get_overview_stats(db: AsyncSession) -> OverviewStats:
        """
        获取概览统计数据

        Args:
            db: 数据库会话

        Returns:
            OverviewStats: 概览统计数据，包含：
            - total_opportunities: 总机会数
            - by_type: 按类型统计 {developer_program: 10, competition: 20, ...}
            - by_source: 按来源统计 {GitHub: 50, Kaggle: 30, ...}
            - active_count: 活跃机会数（status='active'）
            - expiring_soon: 即将截止的数量（7天内）
        """
        # 获取总机会数
        total_query = select(func.count()).select_from(Opportunity).where(
            Opportunity.status != "deleted"
        )
        total_result = await db.execute(total_query)
        total_opportunities = total_result.scalar() or 0

        # 按类型统计
        type_query = (
            select(Opportunity.type, func.count().label("count"))
            .where(Opportunity.status != "deleted")
            .group_by(Opportunity.type)
        )
        type_result = await db.execute(type_query)
        by_type = {row.type: row.count for row in type_result.fetchall()}

        # 按来源统计
        source_query = (
            select(Opportunity.source, func.count().label("count"))
            .where(Opportunity.status != "deleted")
            .group_by(Opportunity.source)
        )
        source_result = await db.execute(source_query)
        by_source = {row.source: row.count for row in source_result.fetchall()}

        # 获取活跃机会数
        active_query = select(func.count()).select_from(Opportunity).where(
            and_(Opportunity.status == "active", Opportunity.status != "deleted")
        )
        active_result = await db.execute(active_query)
        active_count = active_result.scalar() or 0

        # 获取即将截止的数量（7天内）
        now = datetime.now()
        seven_days_later = now + timedelta(days=7)
        expiring_query = select(func.count()).select_from(Opportunity).where(
            and_(
                Opportunity.status != "deleted",
                Opportunity.deadline.isnot(None),
                Opportunity.deadline >= now,
                Opportunity.deadline <= seven_days_later,
            )
        )
        expiring_result = await db.execute(expiring_query)
        expiring_soon = expiring_result.scalar() or 0

        return OverviewStats(
            total_opportunities=total_opportunities,
            by_type=by_type,
            by_source=by_source,
            active_count=active_count,
            expiring_soon=expiring_soon,
        )

    @staticmethod
    async def get_trend_data(
        db: AsyncSession,
        days: int = 30,
        group_by: str = "day",  # day, week, month
    ) -> TrendDataResponse:
        """
        获取趋势数据

        Args:
            db: 数据库会话
            days: 统计天数
            group_by: 分组方式（day, week, month）

        Returns:
            TrendDataResponse: 趋势数据响应，包含：
            - date: 日期
            - count: 新增数量
            - by_type: 按类型分组
        """
        # 计算起始日期
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)

        # 根据分组方式选择日期格式化函数（使用 strftime 兼容 SQLite）
        if group_by == "week":
            # 按周分组：使用 strftime 格式化为年-周
            date_format = func.strftime("%Y-%W", Opportunity.created_at)
        elif group_by == "month":
            # 按月分组
            date_format = func.strftime("%Y-%m", Opportunity.created_at)
        else:
            # 按天分组（默认）
            date_format = func.strftime("%Y-%m-%d", Opportunity.created_at)

        # 查询每日新增数量
        trend_query = (
            select(
                date_format.label("date"),
                func.count().label("count"),
            )
            .where(
                and_(
                    Opportunity.status != "deleted",
                    cast(Opportunity.created_at, Date) >= start_date,
                    cast(Opportunity.created_at, Date) <= end_date,
                )
            )
            .group_by(text("date"))
            .order_by(text("date"))
        )

        trend_result = await db.execute(trend_query)
        trend_rows = trend_result.fetchall()

        # 查询每日按类型分组的数量
        type_trend_query = (
            select(
                date_format.label("date"),
                Opportunity.type,
                func.count().label("count"),
            )
            .where(
                and_(
                    Opportunity.status != "deleted",
                    cast(Opportunity.created_at, Date) >= start_date,
                    cast(Opportunity.created_at, Date) <= end_date,
                )
            )
            .group_by(text("date"), Opportunity.type)
            .order_by(text("date"))
        )

        type_trend_result = await db.execute(type_trend_query)
        type_trend_rows = type_trend_result.fetchall()

        # 构建日期到类型的映射
        date_type_map: dict[str, dict[str, int]] = {}
        for row in type_trend_rows:
            date_key = row.date
            type_name = row.type
            count = row.count
            if date_key not in date_type_map:
                date_type_map[date_key] = {}
            date_type_map[date_key][type_name] = count

        # 组装结果
        data_points: list[TrendDataPoint] = []
        total_count = 0
        for row in trend_rows:
            date_key = row.date
            count = row.count
            total_count += count
            by_type = date_type_map.get(date_key, {})
            data_points.append(
                TrendDataPoint(
                    date=date_key,
                    count=count,
                    by_type=by_type,
                )
            )

        return TrendDataResponse(
            data=data_points,
            total=total_count,
        )

    @staticmethod
    async def get_source_distribution(db: AsyncSession) -> DistributionResponse:
        """
        获取来源分布

        Args:
            db: 数据库会话

        Returns:
            DistributionResponse: 来源分布响应，包含：
            - source: 来源名称
            - count: 数量
            - percentage: 百分比
        """
        # 查询总数
        total_query = select(func.count()).select_from(Opportunity).where(
            Opportunity.status != "deleted"
        )
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 1  # 避免除以零

        # 按来源统计
        source_query = (
            select(Opportunity.source, func.count().label("count"))
            .where(Opportunity.status != "deleted")
            .group_by(Opportunity.source)
            .order_by(func.count().desc())
        )
        source_result = await db.execute(source_query)
        source_rows = source_result.fetchall()

        items: list[DistributionItem] = []
        for row in source_rows:
            percentage = round((row.count / total) * 100, 2)
            items.append(
                DistributionItem(
                    name=row.source,
                    count=row.count,
                    percentage=percentage,
                )
            )

        return DistributionResponse(
            items=items,
            total=total,
        )

    @staticmethod
    async def get_type_distribution(db: AsyncSession) -> DistributionResponse:
        """
        获取类型分布

        Args:
            db: 数据库会话

        Returns:
            DistributionResponse: 类型分布响应
        """
        # 查询总数
        total_query = select(func.count()).select_from(Opportunity).where(
            Opportunity.status != "deleted"
        )
        total_result = await db.execute(total_query)
        total = total_result.scalar() or 1  # 避免除以零

        # 按类型统计
        type_query = (
            select(Opportunity.type, func.count().label("count"))
            .where(Opportunity.status != "deleted")
            .group_by(Opportunity.type)
            .order_by(func.count().desc())
        )
        type_result = await db.execute(type_query)
        type_rows = type_result.fetchall()

        items: list[DistributionItem] = []
        for row in type_rows:
            percentage = round((row.count / total) * 100, 2)
            items.append(
                DistributionItem(
                    name=row.type,
                    count=row.count,
                    percentage=percentage,
                )
            )

        return DistributionResponse(
            items=items,
            total=total,
        )

    @staticmethod
    async def get_tag_cloud(db: AsyncSession, limit: int = 50) -> TagCloudResponse:
        """
        获取标签云数据

        Args:
            db: 数据库会话
            limit: 返回数量限制

        Returns:
            TagCloudResponse: 标签云响应，包含：
            - tag: 标签名
            - count: 出现次数
            - size: 相对大小（1-5）
        """
        # 获取所有标签并统计频率（兼容 SQLite 和 PostgreSQL）
        query = select(Opportunity.tags).where(
            Opportunity.status != "deleted",
            Opportunity.tags.isnot(None)
        )
        result = await db.execute(query)
        
        # 在 Python 中统计标签频率
        tag_counts: dict[str, int] = {}
        for row in result.fetchall():
            tags = row[0]
            if tags:
                for tag in tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        if not tag_counts:
            return TagCloudResponse(items=[])
        
        # 按频率排序
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        if not sorted_tags:
            return TagCloudResponse(items=[])
        
        # 计算标签大小（1-5）
        max_count = sorted_tags[0][1]
        min_count = sorted_tags[-1][1]
        count_range = max_count - min_count if max_count != min_count else 1

        items: list[TagCloudItem] = []
        for tag_name, count in sorted_tags:
            # 计算相对大小（1-5）
            if count_range == 0:
                size = 3
            else:
                # 线性映射到 1-5
                normalized = (count - min_count) / count_range
                size = int(round(normalized * 4 + 1))  # 1-5

            items.append(
                TagCloudItem(
                    tag=tag_name,
                    count=count,
                    size=size,
                )
            )

        return TagCloudResponse(items=items)

    @staticmethod
    async def get_deadline_calendar(
        db: AsyncSession,
        start_date: date,
        end_date: date,
    ) -> CalendarResponse:
        """
        获取截止日期日历数据

        Args:
            db: 数据库会话
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            CalendarResponse: 日历响应，返回指定日期范围内有机会截止的日期列表
        """
        # 查询指定日期范围内截止的机会
        query = (
            select(Opportunity)
            .where(
                and_(
                    Opportunity.status != "deleted",
                    Opportunity.deadline.isnot(None),
                    cast(Opportunity.deadline, Date) >= start_date,
                    cast(Opportunity.deadline, Date) <= end_date,
                )
            )
            .order_by(Opportunity.deadline)
        )

        result = await db.execute(query)
        opportunities = result.scalars().all()

        # 按日期分组
        date_opportunities: dict[str, list[CalendarOpportunity]] = {}
        for opp in opportunities:
            if opp.deadline:
                date_key = opp.deadline.strftime("%Y-%m-%d")
                if date_key not in date_opportunities:
                    date_opportunities[date_key] = []
                date_opportunities[date_key].append(
                    CalendarOpportunity(
                        id=opp.id,
                        title=opp.title,
                        type=opp.type,
                        source=opp.source,
                        deadline=opp.deadline.strftime("%Y-%m-%d %H:%M:%S") if opp.deadline else None,
                    )
                )

        # 构建事件列表
        events: list[CalendarEvent] = []
        for date_key in sorted(date_opportunities.keys()):
            events.append(
                CalendarEvent(
                    date=date_key,
                    opportunities=date_opportunities[date_key],
                )
            )

        return CalendarResponse(
            events=events,
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )
