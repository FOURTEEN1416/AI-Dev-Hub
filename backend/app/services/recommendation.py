"""
智能推荐服务
实现基于协同过滤、内容过滤和热门推荐的混合推荐算法
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import func, select, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.opportunity import Opportunity
from app.models.user_behavior import UserBehavior
from app.models.user_subscription import UserSubscription
from app.schemas.recommendation import (
    UserBehaviorCreate,
    UserSubscriptionUpdate,
    RecommendedOpportunity,
)

if TYPE_CHECKING:
    from app.models.user import User


class RecommendationService:
    """智能推荐服务
    
    推荐算法：
    1. 协同过滤：基于用户行为相似度
    2. 内容过滤：基于用户偏好匹配
    3. 热门推荐：基于全局热度
    4. 时间衰减：近期行为权重更高
    """

    # 行为类型权重配置
    BEHAVIOR_WEIGHTS = {
        "view": 1.0,      # 浏览权重最低
        "click": 2.0,     # 点击权重中等
        "favorite": 5.0,  # 收藏权重较高
        "share": 3.0,     # 分享权重中等偏高
    }

    # 时间衰减系数（天）
    TIME_DECAY_FACTOR = 30

    @staticmethod
    async def record_behavior(
        db: AsyncSession,
        user_id: int,
        behavior: UserBehaviorCreate
    ) -> UserBehavior:
        """记录用户行为
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            behavior: 行为数据
            
        Returns:
            创建的用户行为记录
        """
        user_behavior = UserBehavior(
            user_id=user_id,
            opportunity_id=behavior.opportunity_id,
            behavior_type=behavior.behavior_type,
            duration=behavior.duration,
        )
        db.add(user_behavior)
        await db.commit()
        await db.refresh(user_behavior)
        return user_behavior

    @staticmethod
    async def get_user_behaviors(
        db: AsyncSession,
        user_id: int,
        limit: int = 100
    ) -> list[UserBehavior]:
        """获取用户行为历史
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 返回记录数量限制
            
        Returns:
            用户行为记录列表
        """
        stmt = (
            select(UserBehavior)
            .where(UserBehavior.user_id == user_id)
            .order_by(desc(UserBehavior.created_at))
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_recommendations(
        db: AsyncSession,
        user_id: int,
        limit: int = 10
    ) -> list[RecommendedOpportunity]:
        """获取个性化推荐
        
        算法流程：
        1. 获取用户偏好（订阅设置）
        2. 获取用户行为历史
        3. 计算内容相似度得分
        4. 计算协同过滤得分
        5. 融合得分并排序
        6. 生成推荐理由
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            limit: 返回推荐数量
            
        Returns:
            推荐机会列表
        """
        # 1. 获取用户订阅偏好
        subscription = await RecommendationService.get_user_subscription(db, user_id)
        
        # 2. 获取用户行为历史
        behaviors = await RecommendationService.get_user_behaviors(db, user_id, limit=50)
        
        # 3. 获取用户已交互的机会ID（避免重复推荐）
        interacted_ids = {b.opportunity_id for b in behaviors}
        
        # 4. 获取所有活跃机会
        stmt = (
            select(Opportunity)
            .where(Opportunity.status == "active")
            .order_by(desc(Opportunity.created_at))
            .limit(100)
        )
        result = await db.execute(stmt)
        all_opportunities = list(result.scalars().all())
        
        # 5. 计算每个机会的推荐分数
        recommendations = []
        user_preferences = {
            "types": subscription.preferred_types if subscription else [],
            "sources": subscription.preferred_sources if subscription else [],
            "tags": subscription.preferred_tags if subscription else [],
            "behaviors": behaviors,
        }
        
        for opp in all_opportunities:
            # 跳过已交互的机会
            if opp.id in interacted_ids:
                continue
            
            # 计算内容匹配分数
            content_score = RecommendationService.calculate_content_score(
                opp,
                user_preferences.get("types", []) or [],
                user_preferences.get("sources", []) or [],
                user_preferences.get("tags", []) or [],
            )
            
            # 计算协同过滤分数
            collab_score = await RecommendationService._calculate_collaborative_score(
                db, user_id, opp, behaviors
            )
            
            # 计算热度分数
            popularity_score = await RecommendationService._calculate_popularity_score(db, opp)
            
            # 融合分数（加权平均）
            # 内容匹配权重 0.5，协同过滤权重 0.3，热度权重 0.2
            final_score = (
                content_score * 0.5 +
                collab_score * 0.3 +
                popularity_score * 0.2
            )
            
            # 生成推荐理由
            reason = RecommendationService.generate_recommendation_reason(opp, user_preferences)
            
            recommendations.append(RecommendedOpportunity(
                opportunity=opp,
                score=round(final_score, 3),
                reason=reason,
            ))
        
        # 6. 按分数排序并返回
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]

    @staticmethod
    async def _calculate_collaborative_score(
        db: AsyncSession,
        user_id: int,
        opportunity: Opportunity,
        user_behaviors: list[UserBehavior]
    ) -> float:
        """计算协同过滤分数
        
        基于相似用户的行为计算推荐分数
        
        Args:
            db: 数据库会话
            user_id: 当前用户ID
            opportunity: 目标机会
            user_behaviors: 当前用户的行为历史
            
        Returns:
            协同过滤分数（0-1）
        """
        if not user_behaviors:
            return 0.0
        
        # 获取与当前用户有相似行为的用户
        # 这些用户与当前用户浏览/收藏过相同的机会
        interacted_ids = [b.opportunity_id for b in user_behaviors]
        
        if not interacted_ids:
            return 0.0
        
        # 查找有相似行为的用户
        stmt = (
            select(UserBehavior.user_id)
            .where(
                UserBehavior.opportunity_id.in_(interacted_ids),
                UserBehavior.user_id != user_id
            )
            .distinct()
        )
        result = await db.execute(stmt)
        similar_user_ids = [row[0] for row in result.all()]
        
        if not similar_user_ids:
            return 0.0
        
        # 检查这些相似用户是否与目标机会有交互
        stmt = (
            select(func.count(UserBehavior.id))
            .where(
                UserBehavior.user_id.in_(similar_user_ids),
                UserBehavior.opportunity_id == opportunity.id
            )
        )
        result = await db.execute(stmt)
        interaction_count = result.scalar() or 0
        
        # 归一化分数
        max_expected = len(similar_user_ids)
        if max_expected == 0:
            return 0.0
        
        return min(1.0, interaction_count / max_expected)

    @staticmethod
    async def _calculate_popularity_score(db: AsyncSession, opportunity: Opportunity) -> float:
        """计算热度分数
        
        基于全局交互量计算热度
        
        Args:
            db: 数据库会话
            opportunity: 目标机会
            
        Returns:
            热度分数（0-1）
        """
        # 获取该机会的总交互量
        stmt = (
            select(func.count(UserBehavior.id))
            .where(UserBehavior.opportunity_id == opportunity.id)
        )
        result = await db.execute(stmt)
        interaction_count = result.scalar() or 0
        
        # 获取所有机会的平均交互量作为基准
        stmt = (
            select(func.count(UserBehavior.id))
            .select_from(UserBehavior)
        )
        result = await db.execute(stmt)
        total_interactions = result.scalar() or 1
        
        stmt = select(func.count(Opportunity.id))
        result = await db.execute(stmt)
        total_opportunities = result.scalar() or 1
        
        avg_interactions = total_interactions / max(total_opportunities, 1)
        
        # 计算相对热度
        if avg_interactions == 0:
            return 0.0
        
        return min(1.0, interaction_count / (avg_interactions * 2))

    @staticmethod
    async def get_similar_opportunities(
        db: AsyncSession,
        opportunity_id: int,
        limit: int = 5
    ) -> list[Opportunity]:
        """获取相似机会（基于标签和类型）
        
        Args:
            db: 数据库会话
            opportunity_id: 目标机会ID
            limit: 返回数量限制
            
        Returns:
            相似机会列表
        """
        # 获取目标机会
        stmt = select(Opportunity).where(Opportunity.id == opportunity_id)
        result = await db.execute(stmt)
        target = result.scalar_one_or_none()
        
        if not target:
            return []
        
        # 查找具有相同类型或标签的机会
        stmt = (
            select(Opportunity)
            .where(
                Opportunity.id != opportunity_id,
                Opportunity.status == "active",
                or_(
                    Opportunity.type == target.type,
                    Opportunity.tags.overlap(target.tags) if target.tags else False
                )
            )
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_trending_opportunities(
        db: AsyncSession,
        days: int = 7,
        limit: int = 10
    ) -> list[Opportunity]:
        """获取热门机会
        
        基于近期的用户交互量计算热度
        
        Args:
            db: 数据库会话
            days: 统计天数
            limit: 返回数量限制
            
        Returns:
            热门机会列表
        """
        # 计算时间范围
        start_date = datetime.now() - timedelta(days=days)
        
        # 查询近期交互最多的机会
        stmt = (
            select(
                Opportunity,
                func.count(UserBehavior.id).label("interaction_count")
            )
            .join(UserBehavior, UserBehavior.opportunity_id == Opportunity.id, isouter=True)
            .where(
                Opportunity.status == "active",
                or_(
                    UserBehavior.created_at >= start_date,
                    UserBehavior.id.is_(None)
                )
            )
            .group_by(Opportunity.id)
            .order_by(desc("interaction_count"), desc(Opportunity.created_at))
            .limit(limit)
        )
        result = await db.execute(stmt)
        rows = result.all()
        
        # 返回机会列表
        return [row[0] for row in rows]

    @staticmethod
    async def update_user_subscription(
        db: AsyncSession,
        user_id: int,
        data: UserSubscriptionUpdate
    ) -> UserSubscription:
        """更新用户订阅偏好
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            data: 更新数据
            
        Returns:
            更新后的订阅偏好
        """
        # 查找现有订阅
        stmt = select(UserSubscription).where(UserSubscription.user_id == user_id)
        result = await db.execute(stmt)
        subscription = result.scalar_one_or_none()
        
        if subscription:
            # 更新现有订阅
            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(subscription, key, value)
        else:
            # 创建新订阅
            subscription = UserSubscription(
                user_id=user_id,
                preferred_types=data.preferred_types,
                preferred_sources=data.preferred_sources,
                preferred_tags=data.preferred_tags,
                email_notification=data.email_notification or False,
                notification_frequency=data.notification_frequency or "daily",
            )
            db.add(subscription)
        
        await db.commit()
        await db.refresh(subscription)
        return subscription

    @staticmethod
    async def get_user_subscription(
        db: AsyncSession,
        user_id: int
    ) -> UserSubscription | None:
        """获取用户订阅偏好
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            用户订阅偏好，不存在则返回 None
        """
        stmt = select(UserSubscription).where(UserSubscription.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    def calculate_content_score(
        opportunity: Opportunity,
        preferred_types: list[str],
        preferred_sources: list[str],
        preferred_tags: list[str]
    ) -> float:
        """计算内容匹配分数
        
        根据用户偏好与机会属性的匹配程度计算分数
        
        Args:
            opportunity: 目标机会
            preferred_types: 用户偏好的类型列表
            preferred_sources: 用户偏好的来源列表
            preferred_tags: 用户偏好的标签列表
            
        Returns:
            内容匹配分数（0-1）
        """
        if not preferred_types and not preferred_sources and not preferred_tags:
            # 没有偏好设置时返回中等分数
            return 0.5
        
        score = 0.0
        total_weight = 0.0
        
        # 类型匹配（权重 0.3）
        if preferred_types:
            total_weight += 0.3
            if opportunity.type in preferred_types:
                score += 0.3
        
        # 来源匹配（权重 0.3）
        if preferred_sources:
            total_weight += 0.3
            if opportunity.source in preferred_sources:
                score += 0.3
        
        # 标签匹配（权重 0.4）
        if preferred_tags and opportunity.tags:
            total_weight += 0.4
            # 计算标签重叠率
            matching_tags = set(opportunity.tags) & set(preferred_tags)
            if matching_tags:
                tag_score = len(matching_tags) / min(len(opportunity.tags), len(preferred_tags))
                score += 0.4 * tag_score
        
        # 归一化分数
        if total_weight == 0:
            return 0.5
        
        return score / total_weight

    @staticmethod
    def generate_recommendation_reason(
        opportunity: Opportunity,
        user_preferences: dict
    ) -> str:
        """生成推荐理由
        
        根据匹配情况生成人类可读的推荐理由
        
        Args:
            opportunity: 目标机会
            user_preferences: 用户偏好字典
            
        Returns:
            推荐理由字符串
        """
        reasons = []
        
        preferred_types = user_preferences.get("types", []) or []
        preferred_sources = user_preferences.get("sources", []) or []
        preferred_tags = user_preferences.get("tags", []) or []
        
        # 类型匹配理由
        if preferred_types and opportunity.type in preferred_types:
            type_names = {
                "developer_program": "开发者计划",
                "competition": "竞赛",
                "free_credits": "免费额度",
                "community": "社区活动",
            }
            reasons.append(f"符合您感兴趣的{type_names.get(opportunity.type, opportunity.type)}类型")
        
        # 来源匹配理由
        if preferred_sources and opportunity.source in preferred_sources:
            reasons.append(f"来自您关注的平台「{opportunity.source}」")
        
        # 标签匹配理由
        if preferred_tags and opportunity.tags:
            matching_tags = set(opportunity.tags) & set(preferred_tags)
            if matching_tags:
                tags_str = "、".join(list(matching_tags)[:3])
                reasons.append(f"包含您感兴趣的标签：{tags_str}")
        
        # 如果没有特定匹配，返回默认理由
        if not reasons:
            reasons.append("根据您的浏览历史推荐")
        
        return "；".join(reasons)
