"""
认证（Auth）API 路由
提供用户注册、登录、信息获取和更新等接口
"""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.user import (
    Token,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["用户认证"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="用户注册")
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    用户注册

    - **email**: 邮箱地址（必填，唯一）
    - **username**: 用户名（可选，唯一）
    - **password**: 密码（必填，6-100位）
    """
    user_service = UserService(db)

    # 检查邮箱是否已注册
    if await user_service.check_email_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册",
        )

    # 检查用户名是否已使用
    if user_data.username and await user_service.check_username_exists(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被使用",
        )

    # 创建用户
    user = await user_service.create_user(user_data)

    return UserResponse.model_validate(user)


@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    用户登录，返回 JWT 访问令牌

    - **email**: 邮箱地址
    - **password**: 密码
    """
    user_service = UserService(db)

    # 验证用户
    user = await user_service.authenticate_user(user_data.email, user_data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户账号已被禁用",
        )

    # 更新最后登录时间
    await user_service.update_user_login_time(user)

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_id": user.id, "email": user.email},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout", summary="用户登出")
async def logout(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    用户登出

    注意：由于 JWT 是无状态的，服务端不会存储 token 状态。
    客户端需要自行删除本地存储的 token。
    如需实现服务端 token 失效，需要额外实现 token 黑名单机制。
    """
    return {"message": "登出成功", "detail": "请删除本地存储的访问令牌"}


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """
    获取当前登录用户的详细信息
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse, summary="更新用户信息")
async def update_user_info(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    更新当前用户信息

    - **username**: 新用户名（可选）
    - **password**: 新密码（可选，6-100位）
    """
    user_service = UserService(db)

    # 更新用户名
    if update_data.username is not None:
        # 检查用户名是否已被其他用户使用
        existing_user = await user_service.get_user_by_username(update_data.username)
        if existing_user is not None and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该用户名已被使用",
            )
        await user_service.update_user_username(current_user, update_data.username)

    # 更新密码
    if update_data.password is not None:
        await user_service.update_user_password(current_user, update_data.password)

    # 刷新用户数据
    await db.refresh(current_user)

    return UserResponse.model_validate(current_user)
