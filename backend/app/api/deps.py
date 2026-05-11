"""
API 依赖注入模块
提供数据库会话和用户认证等公共依赖
"""

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.services.user import UserService

# OAuth2 密码模式（用于 Swagger 文档）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

# JWT Bearer 安全方案
security = HTTPBearer(auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    获取当前登录用户（必须认证）

    Args:
        token: JWT 令牌
        db: 数据库会话

    Returns:
        当前用户实例

    Raises:
        HTTPException: 未认证或用户不存在
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if token is None:
        raise credentials_exception

    # 导入安全模块（避免循环导入）
    from app.core.security import decode_token

    # 解析 token
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id: int | None = payload.get("user_id")
    if user_id is None:
        raise credentials_exception

    # 查询用户
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    获取当前活跃用户

    Args:
        current_user: 当前用户

    Returns:
        当前活跃用户实例

    Raises:
        HTTPException: 用户已被禁用
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账号已被禁用",
        )
    return current_user


async def get_optional_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    获取可选的当前用户（未登录也能访问）

    Args:
        token: JWT 令牌（可选）
        db: 数据库会话

    Returns:
        用户实例，未登录返回 None
    """
    if token is None:
        return None

    # 导入安全模块（避免循环导入）
    from app.core.security import decode_token

    # 解析 token
    payload = decode_token(token)
    if payload is None:
        return None

    user_id: int | None = payload.get("user_id")
    if user_id is None:
        return None

    # 查询用户
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)

    return user
