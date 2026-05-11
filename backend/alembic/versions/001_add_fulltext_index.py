"""添加全文搜索索引

Revision ID: 001
Revises: 
Create Date: 2025-05-11

添加 PostgreSQL 全文搜索索引，支持中文分词
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级数据库：添加全文搜索索引"""
    # 创建全文搜索索引
    # 使用 'simple' 配置支持中文分词
    # 将 title 和 description 合并后建立索引
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_opportunities_fulltext
        ON opportunities
        USING gin(to_tsvector('simple', title || ' ' || COALESCE(description, '')))
    """)


def downgrade() -> None:
    """降级数据库：删除全文搜索索引"""
    op.execute("""
        DROP INDEX IF EXISTS ix_opportunities_fulltext
    """)
