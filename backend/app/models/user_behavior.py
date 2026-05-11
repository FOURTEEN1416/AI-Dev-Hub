"""
用户行为（UserBehavior）数据模型
记录用户行为，用于推荐算法
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.opportunity import Opportunity
    from app.models.user import User


class UserBehavior(Base):
    """用户行为记录，用于推荐算法"""

    __tablename__ = "user_behaviors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), index=True, nullable=False, comment="用户ID"
    )
    opportunity_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("opportunities.id"), index=True, nullable=False, comment="机会ID"
    )
    behavior_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="行为类型：view/favorite/click/share"
    )
    duration: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="停留时间（秒）"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )

    # 关系
    user: Mapped["User"] = relationship(lazy="selectin")
    opportunity: Mapped["Opportunity"] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return f"<UserBehavior(id={self.id}, user_id={self.user_id}, behavior_type='{self.behavior_type}')>"
