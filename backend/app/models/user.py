"""
用户（User）数据模型
定义用户的数据表结构
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user_favorite import UserFavorite


class User(Base):
    """用户模型，存储用户账户信息"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False, comment="邮箱地址")
    username: Mapped[str | None] = mapped_column(String(100), unique=True, index=True, nullable=True, comment="用户名")
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False, comment="加密后的密码")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment="是否激活")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment="是否超级管理员")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="最后登录时间")

    # 关系：用户的收藏列表
    favorites: Mapped[list["UserFavorite"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
