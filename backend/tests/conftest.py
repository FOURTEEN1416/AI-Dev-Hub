"""
测试配置和fixtures
提供测试所需的数据库会话、客户端和测试数据
"""

import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db

# 测试数据库URL（使用SQLite内存数据库）
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环，用于整个测试会话"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """创建测试数据库引擎"""
    # 使用 StaticPool 确保内存数据库在测试期间保持连接
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 测试结束后删除所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine):
    """创建测试数据库会话"""
    async_session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with async_session_factory() as session:
        yield session


@pytest.fixture(scope="function")
async def client(db_session):
    """创建测试客户端，使用测试数据库会话"""
    async def override_get_db():
        yield db_session
    
    # 覆盖数据库依赖
    app.dependency_overrides[get_db] = override_get_db
    
    # 创建异步客户端
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # 清理依赖覆盖
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """测试用户数据"""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Test123456"
    }


@pytest.fixture
async def auth_client(client, test_user_data):
    """已认证的测试客户端"""
    # 注册用户
    await client.post("/api/v1/auth/register", json=test_user_data)
    
    # 登录获取token
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    
    # 设置认证头
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    
    return client


@pytest.fixture
def test_opportunity_data():
    """测试机会数据"""
    return {
        "title": "测试机会",
        "type": "competition",
        "source": "TestSource",
        "description": "这是一个测试机会的描述",
        "tags": ["AI", "测试"],
        "status": "active"
    }
