"""
机会（Opportunity）API 路由
提供机会的增删改查和搜索接口
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.opportunity import (
    OpportunityAdvancedFilter,
    OpportunityCreate,
    OpportunityListResponse,
    OpportunityResponse,
)
from app.services.opportunity import OpportunityService

router = APIRouter(prefix="/opportunities", tags=["机会管理"])


@router.get("", response_model=OpportunityListResponse, summary="获取机会列表")
async def get_opportunities(
    type: Optional[str] = Query(None, description="按类型筛选：developer_program/competition/free_credits/community"),
    source: Optional[str] = Query(None, description="按来源筛选"),
    status_filter: Optional[str] = Query(None, alias="status", description="按状态筛选：active/closed/expired"),
    tags: Optional[str] = Query(None, description="按标签筛选，多个标签用逗号分隔"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
) -> OpportunityListResponse:
    """
    获取机会列表，支持多条件筛选和分页

    - **type**: 按机会类型筛选
    - **source**: 按来源平台筛选
    - **status**: 按状态筛选
    - **tags**: 按标签筛选（逗号分隔多个标签）
    - **keyword**: 关键词模糊搜索
    - **page**: 页码，从 1 开始
    - **limit**: 每页数量，最大 100
    """
    tag_list = tags.split(",") if tags else None
    service = OpportunityService(db)
    return await service.get_opportunities(
        filters={
            "type": type,
            "source": source,
            "status": status_filter,
            "tags": tag_list,
            "keyword": keyword,
        },
        page=page,
        limit=limit,
    )


@router.get("/search", response_model=OpportunityListResponse, summary="搜索机会")
async def search_opportunities(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
) -> OpportunityListResponse:
    """
    全文搜索机会

    - **keyword**: 搜索关键词，在标题和描述中搜索
    - **page**: 页码，从 1 开始
    - **limit**: 每页数量，最大 100
    """
    service = OpportunityService(db)
    return await service.search_opportunities(keyword=keyword, page=page, limit=limit)


@router.get("/types", response_model=list[str], summary="获取所有机会类型")
async def get_opportunity_types(
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    """获取数据库中所有不重复的机会类型"""
    service = OpportunityService(db)
    return await service.get_distinct_types()


@router.get("/sources", response_model=list[str], summary="获取所有来源")
async def get_opportunity_sources(
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    """获取数据库中所有不重复的来源平台"""
    service = OpportunityService(db)
    return await service.get_distinct_sources()


@router.get("/search/advanced", response_model=OpportunityListResponse, summary="高级搜索")
async def advanced_search(
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    types: Optional[str] = Query(None, description="多选类型，逗号分隔"),
    sources: Optional[str] = Query(None, description="多选来源，逗号分隔"),
    tags: Optional[str] = Query(None, description="多选标签，逗号分隔"),
    status_filter: Optional[str] = Query(None, alias="status", description="状态筛选"),
    has_deadline: Optional[bool] = Query(None, description="是否有截止日期"),
    deadline_start: Optional[str] = Query(None, description="截止日期范围-开始 (ISO格式)"),
    deadline_end: Optional[str] = Query(None, description="截止日期范围-结束 (ISO格式)"),
    created_start: Optional[str] = Query(None, description="创建时间范围-开始 (ISO格式)"),
    created_end: Optional[str] = Query(None, description="创建时间范围-结束 (ISO格式)"),
    sort_by: str = Query("created_at", description="排序字段：created_at/deadline/title"),
    sort_order: str = Query("desc", description="排序方向：asc/desc"),
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
) -> OpportunityListResponse:
    """
    高级搜索 - 支持多条件筛选和排序

    - **keyword**: 搜索关键词
    - **types**: 多选类型筛选，逗号分隔
    - **sources**: 多选来源筛选，逗号分隔
    - **tags**: 多选标签筛选，逗号分隔
    - **status**: 状态筛选
    - **has_deadline**: 是否有截止日期
    - **deadline_start**: 截止日期范围开始
    - **deadline_end**: 截止日期范围结束
    - **created_start**: 创建时间范围开始
    - **created_end**: 创建时间范围结束
    - **sort_by**: 排序字段 (created_at/deadline/title)
    - **sort_order**: 排序方向 (asc/desc)
    - **page**: 页码，从 1 开始
    - **limit**: 每页数量，最大 100
    """
    from datetime import datetime

    # 解析时间参数
    def parse_datetime(value: Optional[str]) -> Optional[datetime]:
        if value:
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
        return None

    # 构建筛选条件
    filters = OpportunityAdvancedFilter(
        keyword=keyword,
        types=types.split(",") if types else None,
        sources=sources.split(",") if sources else None,
        tags=tags.split(",") if tags else None,
        status=status_filter,
        has_deadline=has_deadline,
        deadline_start=parse_datetime(deadline_start),
        deadline_end=parse_datetime(deadline_end),
        created_start=parse_datetime(created_start),
        created_end=parse_datetime(created_end),
        sort_by=sort_by,
        sort_order=sort_order,
    )

    service = OpportunityService(db)
    return await service.get_opportunities_advanced(filters=filters, page=page, limit=limit)


@router.get("/tags/popular", response_model=list[str], summary="获取热门标签")
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    """
    获取热门标签

    统计 tags 数组中出现频率最高的标签

    - **limit**: 返回数量限制，最大 100
    """
    service = OpportunityService(db)
    return await service.get_popular_tags(limit=limit)


@router.get("/sources/recent", response_model=list[str], summary="获取最近活跃的来源")
async def get_recent_sources(
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    """
    获取最近活跃的来源

    按创建时间倒序获取最近活跃的来源平台

    - **limit**: 返回数量限制，最大 50
    """
    service = OpportunityService(db)
    return await service.get_recent_sources(limit=limit)


@router.get("/filters/options", summary="获取所有筛选选项")
async def get_filter_options(
    db: AsyncSession = Depends(get_db),
) -> dict[str, list[str]]:
    """
    获取所有筛选选项（类型、来源、标签）

    返回可用于前端筛选下拉框的所有选项
    """
    service = OpportunityService(db)
    return await service.get_filter_options()


@router.get("/{opportunity_id}", response_model=OpportunityResponse, summary="获取机会详情")
async def get_opportunity(
    opportunity_id: int,
    db: AsyncSession = Depends(get_db),
) -> OpportunityResponse:
    """
    根据ID获取机会详情

    - **opportunity_id**: 机会ID
    """
    service = OpportunityService(db)
    opportunity = await service.get_opportunity(opportunity_id)
    if opportunity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"机会不存在，ID: {opportunity_id}",
        )
    return opportunity


@router.post("", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED, summary="创建机会")
async def create_opportunity(
    data: OpportunityCreate,
    db: AsyncSession = Depends(get_db),
) -> OpportunityResponse:
    """
    创建新的机会记录（主要用于爬虫写入）

    - **title**: 机会标题（必填）
    - **type**: 机会类型（必填）
    - **source**: 来源平台（必填）
    - **description**: 详细描述
    - **tags**: 标签列表
    - **deadline**: 截止日期
    - **reward**: 奖励说明
    - **requirements**: 参与要求
    - **official_link**: 官方链接
    """
    service = OpportunityService(db)
    return await service.create_opportunity(data=data)
