"""
Alembic 迁移环境配置
支持自动生成迁移脚本，对比 SQLAlchemy 模型与数据库的差异
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import settings
from app.core.database import Base

# 导入所有模型，确保 Base.metadata 包含所有表的元数据
from app.models import Opportunity  # noqa: F401

# Alembic Config 对象
config = context.config

# 设置日志
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 设置同步数据库 URL（Alembic 迁移使用同步连接）
config.set_main_option("sqlalchemy.url", settings.SYNC_DATABASE_URL)

# 元数据目标，用于 autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    以 'offline' 模式运行迁移
    仅生成 SQL 脚本，不需要连接数据库
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """执行迁移操作"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    以 'online' 模式运行异步迁移
    创建异步引擎并执行迁移
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """以 'online' 模式运行迁移的入口"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
