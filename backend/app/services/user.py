"""
用户（User）业务逻辑层
处理用户相关的所有业务逻辑，包括注册、登录、信息更新等
"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


class UserService:
    """用户业务逻辑服务类"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_user(self, user_data: UserCreate) -> User:
        """
        创建新用户

        Args:
            user_data: 用户注册数据

        Returns:
            新创建的用户模型实例
        """
        # 对密码进行加密
        hashed_password = get_password_hash(user_data.password)

        # 创建用户实例
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False,
        )

        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)

        return user

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """
        验证用户登录

        Args:
            email: 用户邮箱
            password: 明文密码

        Returns:
            验证成功返回用户实例，失败返回 None
        """
        # 查找用户
        user = await self.get_user_by_email(email)

        if user is None:
            return None

        # 验证密码
        if not verify_password(password, user.hashed_password):
            return None

        return user

    async def get_user_by_email(self, email: str) -> User | None:
        """
        根据邮箱获取用户

        Args:
            email: 用户邮箱

        Returns:
            用户实例，不存在返回 None
        """
        query = select(User).where(User.email == email)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        根据 ID 获取用户

        Args:
            user_id: 用户ID

        Returns:
            用户实例，不存在返回 None
        """
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        根据用户名获取用户

        Args:
            username: 用户名

        Returns:
            用户实例，不存在返回 None
        """
        query = select(User).where(User.username == username)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_user_login_time(self, user: User) -> None:
        """
        更新用户最后登录时间

        Args:
            user: 用户实例
        """
        user.last_login = datetime.now(timezone.utc)
        await self.db.flush()

    async def update_user_password(self, user: User, new_password: str) -> None:
        """
        更新用户密码

        Args:
            user: 用户实例
            new_password: 新密码（明文）
        """
        user.hashed_password = get_password_hash(new_password)
        await self.db.flush()

    async def update_user_username(self, user: User, new_username: str | None) -> None:
        """
        更新用户名

        Args:
            user: 用户实例
            new_username: 新用户名
        """
        user.username = new_username
        await self.db.flush()

    async def check_email_exists(self, email: str) -> bool:
        """
        检查邮箱是否已被注册

        Args:
            email: 邮箱地址

        Returns:
            是否存在
        """
        user = await self.get_user_by_email(email)
        return user is not None

    async def check_username_exists(self, username: str) -> bool:
        """
        检查用户名是否已被使用

        Args:
            username: 用户名

        Returns:
            是否存在
        """
        user = await self.get_user_by_username(username)
        return user is not None
