"""
推荐 API 路由
提供个性化推荐、热门推荐、相似机会等接口
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.opportunity import OpportunityResponse
from app.schemas.recommendation import (
    UserBehaviorCreate,
    UserSubscriptionUpdate,
    UserSubscriptionResponse,
    RecommendedOpportunity,
)
from app.services.recommendation import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("", response_model=list[RecommendedOpportunity])
async def get_recommendations(
    limit: int = Query(10, ge=1, le=50, description="返回推荐数量"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取个性化推荐
    
    基于用户偏好和行为历史生成个性化推荐列表。
    需要用户登录认证。
    
    Args:
        limit: 返回推荐数量，默认10，最大50
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        推荐机会列表，包含推荐分数和推荐理由
    """
    return await RecommendationService.get_recommendations(
        db=db,
        user_id=current_user.id,
        limit=limit
    )


@router.get("/trending", response_model=list[OpportunityResponse])
async def get_trending(
    days: int = Query(7, ge=1, le=30, description="统计天数"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取热门推荐（无需登录）
    
    基于近期的用户交互量计算热度排名。
    无需用户登录即可访问。
    
    Args:
        days: 统计天数，默认7天，最大30天
        limit: 返回数量，默认10，最大50
        db: 数据库会话
        
    Returns:
        热门机会列表
    """
    return await RecommendationService.get_trending_opportunities(
        db=db,
        days=days,
        limit=limit
    )


@router.get("/similar/{opportunity_id}", response_model=list[OpportunityResponse])
async def get_similar(
    opportunity_id: int,
    limit: int = Query(5, ge=1, le=20, description="返回数量"),
    db: AsyncSession = Depends(get_db)
):
    """获取相似机会
    
    基于机会的类型和标签查找相似的机会。
    无需用户登录即可访问。
    
    Args:
        opportunity_id: 目标机会ID
        limit: 返回数量，默认5，最大20
        db: 数据库会话
        
    Returns:
        相似机会列表
    """
    return await RecommendationService.get_similar_opportunities(
        db=db,
        opportunity_id=opportunity_id,
        limit=limit
    )


@router.post("/behavior", status_code=201)
async def record_behavior(
    behavior: UserBehaviorCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """记录用户行为（用于推荐算法）
    
    记录用户对机会的浏览、点击、收藏、分享等行为，
    用于优化个性化推荐算法。
    
    Args:
        behavior: 用户行为数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        创建成功响应
    """
    await RecommendationService.record_behavior(
        db=db,
        user_id=current_user.id,
        behavior=behavior
    )
    return {"message": "行为记录成功"}


@router.get("/subscription", response_model=UserSubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """获取订阅偏好
    
    获取当前用户的订阅偏好设置。
    
    Args:
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        用户订阅偏好设置
    """
    subscription = await RecommendationService.get_user_subscription(
        db=db,
        user_id=current_user.id
    )
    
    if subscription:
        return UserSubscriptionResponse(
            preferred_types=subscription.preferred_types,
            preferred_sources=subscription.preferred_sources,
            preferred_tags=subscription.preferred_tags,
            email_notification=subscription.email_notification,
            notification_frequency=subscription.notification_frequency,
        )
    
    # 返回默认值
    return UserSubscriptionResponse(
        preferred_types=None,
        preferred_sources=None,
        preferred_tags=None,
        email_notification=False,
        notification_frequency="daily",
    )


@router.put("/subscription", response_model=UserSubscriptionResponse)
async def update_subscription(
    data: UserSubscriptionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """更新订阅偏好
    
    更新当前用户的订阅偏好设置。
    
    Args:
        data: 订阅偏好更新数据
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        更新后的订阅偏好设置
    """
    subscription = await RecommendationService.update_user_subscription(
        db=db,
        user_id=current_user.id,
        data=data
    )
    
    return UserSubscriptionResponse(
        preferred_types=subscription.preferred_types,
        preferred_sources=subscription.preferred_sources,
        preferred_tags=subscription.preferred_tags,
        email_notification=subscription.email_notification,
        notification_frequency=subscription.notification_frequency,
    )
