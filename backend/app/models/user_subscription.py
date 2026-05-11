"""
用户订阅（UserSubscription）数据模型
存储用户订阅偏好设置
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class UserSubscription(Base):
    """用户订阅偏好"""

    __tablename__ = "user_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="用户ID"
    )
    preferred_types: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True, comment="感兴趣的类型列表"
    )
    preferred_sources: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True, comment="感兴趣的来源列表"
    )
    preferred_tags: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True, comment="感兴趣的标签列表"
    )
    email_notification: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, comment="是否开启邮件通知"
    )
    notification_frequency: Mapped[str] = mapped_column(
        String(20), default="daily", nullable=False, comment="通知频率：daily/weekly"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    # 关系
    user: Mapped["User"] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return f"<UserSubscription(id={self.id}, user_id={self.user_id})>"
