"""
通知 API 路由
提供通知相关的接口
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.services.notification import NotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


class SubscriptionUpdate(BaseModel):
    """订阅更新请求模型"""
    email_notification: bool | None = None
    notification_frequency: str | None = None
    preferred_types: list[str] | None = None
    preferred_sources: list[str] | None = None
    preferred_tags: list[str] | None = None


class SubscriptionResponse(BaseModel):
    """订阅设置响应模型"""
    id: int
    user_id: int
    email_notification: bool
    notification_frequency: str
    preferred_types: list[str] | None
    preferred_sources: list[str] | None
    preferred_tags: list[str] | None

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str
    success: bool = True


@router.post("/test", response_model=MessageResponse)
async def send_test_notification(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    发送测试通知

    向当前用户发送一封测试邮件，包含最新的几个机会信息

    Args:
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        MessageResponse: 发送结果
    """
    success = await NotificationService.send_test_notification(db, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="测试通知发送失败，请检查邮件配置或稍后重试"
        )

    return MessageResponse(
        message="测试通知已发送到您的邮箱，请查收",
        success=True
    )


@router.post("/subscribe", response_model=SubscriptionResponse)
async def subscribe_notifications(
    update_data: SubscriptionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    订阅通知

    开启或更新用户的邮件通知设置

    Args:
        update_data: 订阅更新数据
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        SubscriptionResponse: 更新后的订阅设置
    """
    # 验证通知频率
    if update_data.notification_frequency and update_data.notification_frequency not in ["daily", "weekly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="通知频率必须是 'daily' 或 'weekly'"
        )

    # 更新订阅设置，默认开启邮件通知
    subscription = await NotificationService.update_subscription(
        db,
        current_user.id,
        email_notification=update_data.email_notification if update_data.email_notification is not None else True,
        notification_frequency=update_data.notification_frequency,
        preferred_types=update_data.preferred_types,
        preferred_sources=update_data.preferred_sources,
        preferred_tags=update_data.preferred_tags
    )

    return SubscriptionResponse(
        id=subscription.id,
        user_id=subscription.user_id,
        email_notification=subscription.email_notification,
        notification_frequency=subscription.notification_frequency,
        preferred_types=subscription.preferred_types,
        preferred_sources=subscription.preferred_sources,
        preferred_tags=subscription.preferred_tags
    )


@router.post("/unsubscribe", response_model=MessageResponse)
async def unsubscribe_notifications(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    取消订阅

    关闭用户的邮件通知

    Args:
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        MessageResponse: 操作结果
    """
    await NotificationService.update_subscription(
        db,
        current_user.id,
        email_notification=False
    )

    return MessageResponse(
        message="已成功取消邮件订阅",
        success=True
    )


@router.get("/settings", response_model=SubscriptionResponse)
async def get_notification_settings(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取通知设置

    获取当前用户的通知偏好设置

    Args:
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        SubscriptionResponse: 当前订阅设置
    """
    subscription = await NotificationService.get_or_create_subscription(db, current_user.id)

    return SubscriptionResponse(
        id=subscription.id,
        user_id=subscription.user_id,
        email_notification=subscription.email_notification,
        notification_frequency=subscription.notification_frequency,
        preferred_types=subscription.preferred_types,
        preferred_sources=subscription.preferred_sources,
        preferred_tags=subscription.preferred_tags
    )


@router.put("/settings", response_model=SubscriptionResponse)
async def update_notification_settings(
    update_data: SubscriptionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    更新通知设置

    更新用户的通知偏好设置

    Args:
        update_data: 更新数据
        current_user: 当前登录用户
        db: 数据库会话

    Returns:
        SubscriptionResponse: 更新后的订阅设置
    """
    # 验证通知频率
    if update_data.notification_frequency and update_data.notification_frequency not in ["daily", "weekly"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="通知频率必须是 'daily' 或 'weekly'"
        )

    subscription = await NotificationService.update_subscription(
        db,
        current_user.id,
        email_notification=update_data.email_notification,
        notification_frequency=update_data.notification_frequency,
        preferred_types=update_data.preferred_types,
        preferred_sources=update_data.preferred_sources,
        preferred_tags=update_data.preferred_tags
    )

    return SubscriptionResponse(
        id=subscription.id,
        user_id=subscription.user_id,
        email_notification=subscription.email_notification,
        notification_frequency=subscription.notification_frequency,
        preferred_types=subscription.preferred_types,
        preferred_sources=subscription.preferred_sources,
        preferred_tags=subscription.preferred_tags
    )
