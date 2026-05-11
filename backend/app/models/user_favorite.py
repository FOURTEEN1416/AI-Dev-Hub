"""
用户收藏（UserFavorite）数据模型
定义用户收藏机会的数据表结构
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.opportunity import Opportunity


class UserFavorite(Base):
    """用户收藏模型，存储用户收藏的机会"""

    __tablename__ = "user_favorites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), index=True, nullable=False, comment="用户ID")
    opportunity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("opportunities.id"), index=True, nullable=False, comment="机会ID"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="收藏时间"
    )

    # 联合唯一约束：同一用户不能重复收藏同一机会
    __table_args__ = (UniqueConstraint("user_id", "opportunity_id", name="uq_user_opportunity"),)

    # 关系
    user: Mapped["User"] = relationship(back_populates="favorites", lazy="selectin")
    opportunity: Mapped["Opportunity"] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return f"<UserFavorite(id={self.id}, user_id={self.user_id}, opportunity_id={self.opportunity_id})>"
