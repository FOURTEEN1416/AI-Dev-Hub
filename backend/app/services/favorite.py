"""
收藏（Favorite）业务逻辑层
处理用户收藏相关的所有业务逻辑
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.opportunity import Opportunity
from app.models.user_favorite import UserFavorite


class FavoriteService:
    """收藏业务逻辑服务类"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def add_favorite(self, user_id: int, opportunity_id: int) -> UserFavorite:
        """
        添加收藏

        Args:
            user_id: 用户ID
            opportunity_id: 机会ID

        Returns:
            新创建的收藏记录
        """
        favorite = UserFavorite(
            user_id=user_id,
            opportunity_id=opportunity_id,
        )

        self.db.add(favorite)
        await self.db.flush()
        await self.db.refresh(favorite)

        return favorite

    async def remove_favorite(self, user_id: int, opportunity_id: int) -> bool:
        """
        取消收藏

        Args:
            user_id: 用户ID
            opportunity_id: 机会ID

        Returns:
            是否成功删除
        """
        query = select(UserFavorite).where(
            UserFavorite.user_id == user_id,
            UserFavorite.opportunity_id == opportunity_id,
        )
        result = await self.db.execute(query)
        favorite = result.scalar_one_or_none()

        if favorite is None:
            return False

        await self.db.delete(favorite)
        await self.db.flush()
        return True

    async def get_user_favorites(
        self,
        user_id: int,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[dict], int]:
        """
        获取用户收藏列表（含机会详情）

        Args:
            user_id: 用户ID
            page: 页码，从 1 开始
            limit: 每页数量

        Returns:
            元组：(收藏列表，总数)
        """
        # 查询总数
        count_query = select(func.count()).select_from(UserFavorite).where(
            UserFavorite.user_id == user_id
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 分页查询收藏记录，同时加载关联的机会信息
        offset = (page - 1) * limit
        query = (
            select(UserFavorite)
            .options(selectinload(UserFavorite.opportunity))
            .where(UserFavorite.user_id == user_id)
            .order_by(UserFavorite.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(query)
        favorites = result.scalars().all()

        # 构建返回数据，包含机会详情
        items = []
        for favorite in favorites:
            opportunity = favorite.opportunity
            if opportunity:
                items.append({
                    "favorite_id": favorite.id,
                    "favorite_created_at": favorite.created_at.isoformat() if favorite.created_at else None,
                    "opportunity": {
                        "id": opportunity.id,
                        "title": opportunity.title,
                        "type": opportunity.type,
                        "source": opportunity.source,
                        "source_url": opportunity.source_url,
                        "description": opportunity.description,
                        "tags": opportunity.tags,
                        "deadline": opportunity.deadline.isoformat() if opportunity.deadline else None,
                        "reward": opportunity.reward,
                        "requirements": opportunity.requirements,
                        "official_link": opportunity.official_link,
                        "status": opportunity.status,
                        "created_at": opportunity.created_at.isoformat() if opportunity.created_at else None,
                        "updated_at": opportunity.updated_at.isoformat() if opportunity.updated_at else None,
                    },
                })

        return items, total

    async def is_favorited(self, user_id: int, opportunity_id: int) -> bool:
        """
        检查用户是否已收藏某个机会

        Args:
            user_id: 用户ID
            opportunity_id: 机会ID

        Returns:
            是否已收藏
        """
        query = select(UserFavorite).where(
            UserFavorite.user_id == user_id,
            UserFavorite.opportunity_id == opportunity_id,
        )
        result = await self.db.execute(query)
        favorite = result.scalar_one_or_none()
        return favorite is not None

    async def check_opportunity_exists(self, opportunity_id: int) -> bool:
        """
        检查机会是否存在

        Args:
            opportunity_id: 机会ID

        Returns:
            是否存在
        """
        query = select(Opportunity).where(Opportunity.id == opportunity_id)
        result = await self.db.execute(query)
        opportunity = result.scalar_one_or_none()
        return opportunity is not None

    async def get_favorite_count(self, user_id: int) -> int:
        """
        获取用户收藏总数

        Args:
            user_id: 用户ID

        Returns:
            收藏数量
        """
        count_query = select(func.count()).select_from(UserFavorite).where(
            UserFavorite.user_id == user_id
        )
        total_result = await self.db.execute(count_query)
        return total_result.scalar() or 0
