"""
机会（Opportunity）数据模型
定义 AI 开发者机会的数据表结构
"""

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text, func, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Opportunity(Base):
    """AI 开发者机会模型，包括开发者计划、竞赛、免费额度、社区活动等"""

    __tablename__ = "opportunities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    title: Mapped[str] = mapped_column(String(500), nullable=False, comment="机会标题")
    type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="机会类型：developer_program/competition/free_credits/community"
    )
    source: Mapped[str] = mapped_column(String(100), nullable=False, comment="来源平台")
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True, comment="来源页面链接")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="详细描述")
    tags: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True, comment="标签列表，使用 JSON 存储"
    )
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, comment="截止日期")
    reward: Mapped[str | None] = mapped_column(Text, nullable=True, comment="奖励说明")
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True, comment="参与要求")
    official_link: Mapped[str | None] = mapped_column(Text, nullable=True, comment="官方链接")
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active", comment="状态：active/closed/expired"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), comment="创建时间"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="更新时间"
    )

    # 普通索引，用于常用查询
    __table_args__ = (
        Index('ix_opportunities_type', type),
        Index('ix_opportunities_source', source),
        Index('ix_opportunities_status', status),
    )

    def __repr__(self) -> str:
        return f"<Opportunity(id={self.id}, title='{self.title}', type='{self.type}')>"
