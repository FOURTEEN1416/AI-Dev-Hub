"""
通知服务模块
提供邮件通知功能，包括每日和每周通知
"""

import logging
from datetime import datetime, timedelta

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.email import email_service
from app.models.opportunity import Opportunity
from app.models.user import User
from app.models.user_subscription import UserSubscription

# 配置日志
logger = logging.getLogger(__name__)


class NotificationService:
    """通知服务"""

    @staticmethod
    async def send_daily_notifications(db: AsyncSession) -> int:
        """
        发送每日通知（定时任务调用）

        Args:
            db: 数据库会话

        Returns:
            int: 成功发送的邮件数量
        """
        logger.info("开始发送每日通知")

        # 获取所有开启了每日邮件通知的用户
        query = (
            select(User, UserSubscription)
            .join(UserSubscription, User.id == UserSubscription.user_id)
            .where(
                User.is_active == True,
                UserSubscription.email_notification == True,
                UserSubscription.notification_frequency == "daily"
            )
        )
        result = await db.execute(query)
        user_subscriptions = result.all()

        sent_count = 0
        since = datetime.utcnow() - timedelta(days=1)

        for user, subscription in user_subscriptions:
            try:
                # 获取用户的新机会
                opportunities = await NotificationService.get_user_new_opportunities(
                    db, user.id, since, subscription
                )

                # 即使没有新机会也发送通知（可选）
                if opportunities:
                    # 转换为字典格式
                    opp_list = [
                        {
                            "title": opp.title,
                            "type": opp.type,
                            "source": opp.source,
                            "deadline": opp.deadline.strftime("%Y-%m-%d") if opp.deadline else None,
                            "description": opp.description,
                            "url": opp.official_link or opp.source_url,
                        }
                        for opp in opportunities[:10]  # 最多发送10个机会
                    ]

                    success = await email_service.send_notification_email(
                        to_email=user.email,
                        username=user.username or user.email,
                        opportunities=opp_list
                    )

                    if success:
                        sent_count += 1
                        logger.info(f"每日通知发送成功: {user.email}")
                    else:
                        logger.warning(f"每日通知发送失败: {user.email}")

            except Exception as e:
                logger.error(f"发送每日通知时出错: {user.email}, 错误: {e}")
                continue

        logger.info(f"每日通知发送完成，共发送 {sent_count} 封邮件")
        return sent_count

    @staticmethod
    async def send_weekly_notifications(db: AsyncSession) -> int:
        """
        发送每周通知

        Args:
            db: 数据库会话

        Returns:
            int: 成功发送的邮件数量
        """
        logger.info("开始发送每周通知")

        # 获取所有开启了每周邮件通知的用户
        query = (
            select(User, UserSubscription)
            .join(UserSubscription, User.id == UserSubscription.user_id)
            .where(
                User.is_active == True,
                UserSubscription.email_notification == True,
                UserSubscription.notification_frequency == "weekly"
            )
        )
        result = await db.execute(query)
        user_subscriptions = result.all()

        sent_count = 0
        since = datetime.utcnow() - timedelta(weeks=1)

        for user, subscription in user_subscriptions:
            try:
                # 获取用户的新机会
                opportunities = await NotificationService.get_user_new_opportunities(
                    db, user.id, since, subscription
                )

                if opportunities:
                    # 转换为字典格式
                    opp_list = [
                        {
                            "title": opp.title,
                            "type": opp.type,
                            "source": opp.source,
                            "deadline": opp.deadline.strftime("%Y-%m-%d") if opp.deadline else None,
                            "description": opp.description,
                            "url": opp.official_link or opp.source_url,
                        }
                        for opp in opportunities[:20]  # 每周最多发送20个机会
                    ]

                    success = await email_service.send_notification_email(
                        to_email=user.email,
                        username=user.username or user.email,
                        opportunities=opp_list
                    )

                    if success:
                        sent_count += 1
                        logger.info(f"每周通知发送成功: {user.email}")
                    else:
                        logger.warning(f"每周通知发送失败: {user.email}")

            except Exception as e:
                logger.error(f"发送每周通知时出错: {user.email}, 错误: {e}")
                continue

        logger.info(f"每周通知发送完成，共发送 {sent_count} 封邮件")
        return sent_count

    @staticmethod
    async def get_user_new_opportunities(
        db: AsyncSession,
        user_id: int,
        since: datetime,
        subscription: UserSubscription | None = None
    ) -> list[Opportunity]:
        """
        获取用户的新机会（根据偏好匹配）

        Args:
            db: 数据库会话
            user_id: 用户ID
            since: 起始时间
            subscription: 用户订阅偏好（可选）

        Returns:
            list[Opportunity]: 匹配的机会列表
        """
        # 基础查询：获取指定时间后创建的活跃机会
        query = select(Opportunity).where(
            Opportunity.status == "active",
            Opportunity.created_at >= since
        )

        # 如果有订阅偏好，进行匹配
        if subscription:
            conditions = []

            # 按类型过滤
            if subscription.preferred_types:
                conditions.append(Opportunity.type.in_(subscription.preferred_types))

            # 按来源过滤
            if subscription.preferred_sources:
                conditions.append(Opportunity.source.in_(subscription.preferred_sources))

            # 按标签过滤（使用数组重叠）
            if subscription.preferred_tags:
                # PostgreSQL 数组重叠操作
                from sqlalchemy import text
                query = query.where(
                    or_(
                        Opportunity.tags.overlap(subscription.preferred_tags),
                        Opportunity.tags == None  # 如果没有标签限制，也包含无标签的机会
                    )
                )

            # 如果有类型或来源条件，应用它们
            if conditions:
                query = query.where(or_(*conditions))

        # 按创建时间倒序排列
        query = query.order_by(Opportunity.created_at.desc())

        result = await db.execute(query)
        opportunities = result.scalars().all()

        return list(opportunities)

    @staticmethod
    async def send_test_notification(
        db: AsyncSession,
        user_id: int
    ) -> bool:
        """
        发送测试通知

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            bool: 发送成功返回True
        """
        # 获取用户信息
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            logger.error(f"用户不存在: {user_id}")
            return False

        # 获取最近的一些机会作为测试内容
        opp_query = (
            select(Opportunity)
            .where(Opportunity.status == "active")
            .order_by(Opportunity.created_at.desc())
            .limit(3)
        )
        opp_result = await db.execute(opp_query)
        opportunities = opp_result.scalars().all()

        # 转换为字典格式
        opp_list = [
            {
                "title": opp.title,
                "type": opp.type,
                "source": opp.source,
                "deadline": opp.deadline.strftime("%Y-%m-%d") if opp.deadline else None,
                "description": opp.description,
                "url": opp.official_link or opp.source_url,
            }
            for opp in opportunities
        ]

        # 发送测试邮件
        success = await email_service.send_notification_email(
            to_email=user.email,
            username=user.username or user.email,
            opportunities=opp_list
        )

        return success

    @staticmethod
    async def get_or_create_subscription(
        db: AsyncSession,
        user_id: int
    ) -> UserSubscription:
        """
        获取或创建用户订阅设置

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            UserSubscription: 用户订阅设置
        """
        query = select(UserSubscription).where(UserSubscription.user_id == user_id)
        result = await db.execute(query)
        subscription = result.scalar_one_or_none()

        if not subscription:
            subscription = UserSubscription(user_id=user_id)
            db.add(subscription)
            await db.commit()
            await db.refresh(subscription)

        return subscription

    @staticmethod
    async def update_subscription(
        db: AsyncSession,
        user_id: int,
        email_notification: bool | None = None,
        notification_frequency: str | None = None,
        preferred_types: list[str] | None = None,
        preferred_sources: list[str] | None = None,
        preferred_tags: list[str] | None = None
    ) -> UserSubscription:
        """
        更新用户订阅设置

        Args:
            db: 数据库会话
            user_id: 用户ID
            email_notification: 是否开启邮件通知
            notification_frequency: 通知频率（daily/weekly）
            preferred_types: 感兴趣的类型列表
            preferred_sources: 感兴趣的来源列表
            preferred_tags: 感兴趣的标签列表

        Returns:
            UserSubscription: 更新后的订阅设置
        """
        subscription = await NotificationService.get_or_create_subscription(db, user_id)

        if email_notification is not None:
            subscription.email_notification = email_notification

        if notification_frequency is not None:
            subscription.notification_frequency = notification_frequency

        if preferred_types is not None:
            subscription.preferred_types = preferred_types

        if preferred_sources is not None:
            subscription.preferred_sources = preferred_sources

        if preferred_tags is not None:
            subscription.preferred_tags = preferred_tags

        await db.commit()
        await db.refresh(subscription)

        return subscription
