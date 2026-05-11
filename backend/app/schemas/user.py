"""
用户（User）Pydantic 数据模式
定义用户相关的请求和响应数据验证模式
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模式，包含基本用户信息"""

    email: EmailStr = Field(..., description="邮箱地址")
    username: Optional[str] = Field(None, max_length=100, description="用户名")


class UserCreate(BaseModel):
    """用户注册请求模式"""

    email: EmailStr = Field(..., description="邮箱地址")
    username: Optional[str] = Field(None, max_length=100, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码（6-100位）")


class UserLogin(BaseModel):
    """用户登录请求模式"""

    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")


class UserUpdate(BaseModel):
    """用户更新请求模式"""

    username: Optional[str] = Field(None, max_length=100, description="用户名")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="新密码（6-100位）")


class UserResponse(BaseModel):
    """用户响应模式，返回给前端的用户信息"""

    id: int = Field(..., description="用户ID")
    email: str = Field(..., description="邮箱地址")
    username: Optional[str] = Field(None, description="用户名")
    is_active: bool = Field(..., description="是否激活")
    is_superuser: bool = Field(..., description="是否超级管理员")
    created_at: datetime = Field(..., description="创建时间")
    last_login: Optional[datetime] = Field(None, description="最后登录时间")

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """JWT Token 响应模式"""

    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")


class TokenData(BaseModel):
    """JWT Token 数据模式，用于解析 token 中的信息"""

    email: Optional[str] = Field(None, description="用户邮箱")
    user_id: Optional[int] = Field(None, description="用户ID")


class UserFavoriteResponse(BaseModel):
    """用户收藏响应模式"""

    id: int = Field(..., description="收藏记录ID")
    opportunity_id: int = Field(..., description="机会ID")
    created_at: datetime = Field(..., description="收藏时间")

    model_config = {"from_attributes": True}


class UserFavoriteListResponse(BaseModel):
    """用户收藏列表分页响应模式"""

    items: list[dict] = Field(..., description="收藏的机会列表（含机会详情）")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    limit: int = Field(..., description="每页数量")
