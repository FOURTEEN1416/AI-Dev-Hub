"""
统计（Statistics）API 路由
提供统计相关的 REST API 接口
"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.statistics import (
    CalendarResponse,
    DistributionResponse,
    OverviewStats,
    TagCloudResponse,
    TrendDataResponse,
)
from app.services.statistics import StatisticsService

# 创建路由器
router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/overview", response_model=OverviewStats, summary="获取概览统计")
async def get_overview(db: AsyncSession = Depends(get_db)) -> OverviewStats:
    """
    获取概览统计数据

    返回:
    - total_opportunities: 总机会数
    - by_type: 按类型统计
    - by_source: 按来源统计
    - active_count: 活跃机会数
    - expiring_soon: 即将截止的数量（7天内）
    """
    return await StatisticsService.get_overview_stats(db)


@router.get("/trend", response_model=TrendDataResponse, summary="获取趋势数据")
async def get_trend(
    days: int = Query(30, ge=1, le=365, description="统计天数"),
    group_by: str = Query("day", pattern="^(day|week|month)$", description="分组方式：day/week/month"),
    db: AsyncSession = Depends(get_db),
) -> TrendDataResponse:
    """
    获取趋势数据

    参数:
    - days: 统计天数（1-365）
    - group_by: 分组方式（day, week, month）

    返回:
    - data: 趋势数据列表
    - total: 总计数量
    """
    return await StatisticsService.get_trend_data(db, days, group_by)


@router.get(
    "/distribution/source",
    response_model=DistributionResponse,
    summary="获取来源分布",
)
async def get_source_distribution(
    db: AsyncSession = Depends(get_db),
) -> DistributionResponse:
    """
    获取来源分布统计

    返回:
    - items: 分布数据列表
    - total: 总计数量
    """
    return await StatisticsService.get_source_distribution(db)


@router.get(
    "/distribution/type",
    response_model=DistributionResponse,
    summary="获取类型分布",
)
async def get_type_distribution(
    db: AsyncSession = Depends(get_db),
) -> DistributionResponse:
    """
    获取类型分布统计

    返回:
    - items: 分布数据列表
    - total: 总计数量
    """
    return await StatisticsService.get_type_distribution(db)


@router.get(
    "/tags/cloud",
    response_model=TagCloudResponse,
    summary="获取标签云",
)
async def get_tag_cloud(
    limit: int = Query(50, ge=10, le=200, description="返回数量限制"),
    db: AsyncSession = Depends(get_db),
) -> TagCloudResponse:
    """
    获取标签云数据

    参数:
    - limit: 返回数量限制（10-200）

    返回:
    - items: 标签云数据列表，包含标签名、出现次数和相对大小（1-5）
    """
    return await StatisticsService.get_tag_cloud(db, limit)


@router.get(
    "/calendar",
    response_model=CalendarResponse,
    summary="获取截止日期日历",
)
async def get_deadline_calendar(
    start_date: date = Query(..., description="开始日期（YYYY-MM-DD）"),
    end_date: date = Query(..., description="结束日期（YYYY-MM-DD）"),
    db: AsyncSession = Depends(get_db),
) -> CalendarResponse:
    """
    获取截止日期日历数据

    参数:
    - start_date: 开始日期
    - end_date: 结束日期

    返回:
    - events: 日历事件列表，每个事件包含日期和当日截止的机会列表
    - start_date: 查询的开始日期
    - end_date: 查询的结束日期
    """
    return await StatisticsService.get_deadline_calendar(db, start_date, end_date)
