"""
推荐（Recommendation）Pydantic 数据模式
定义推荐相关的请求和响应数据验证模式
"""

from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.opportunity import OpportunityResponse


class UserBehaviorCreate(BaseModel):
    """创建用户行为的请求模式"""

    opportunity_id: int = Field(..., description="机会ID")
    behavior_type: str = Field(..., description="行为类型：view/favorite/click/share")
    duration: int | None = Field(None, description="停留时间（秒）")


class UserSubscriptionUpdate(BaseModel):
    """更新用户订阅偏好的请求模式"""

    preferred_types: list[str] | None = Field(None, description="感兴趣的类型列表")
    preferred_sources: list[str] | None = Field(None, description="感兴趣的来源列表")
    preferred_tags: list[str] | None = Field(None, description="感兴趣的标签列表")
    email_notification: bool | None = Field(None, description="是否开启邮件通知")
    notification_frequency: str | None = Field(None, description="通知频率：daily/weekly")


class UserSubscriptionResponse(BaseModel):
    """用户订阅偏好的响应模式"""

    preferred_types: list[str] | None = Field(None, description="感兴趣的类型列表")
    preferred_sources: list[str] | None = Field(None, description="感兴趣的来源列表")
    preferred_tags: list[str] | None = Field(None, description="感兴趣的标签列表")
    email_notification: bool = Field(..., description="是否开启邮件通知")
    notification_frequency: str = Field(..., description="通知频率")

    model_config = {"from_attributes": True}


class RecommendedOpportunity(BaseModel):
    """推荐机会的响应模式"""

    opportunity: OpportunityResponse = Field(..., description="机会详情")
    score: float = Field(..., ge=0.0, le=1.0, description="推荐分数（0-1）")
    reason: str = Field(..., description="推荐理由")
