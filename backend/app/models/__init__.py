"""
数据模型包
导出所有 SQLAlchemy 模型，确保 Alembic 迁移能正确识别
"""

from app.models.opportunity import Opportunity
from app.models.user import User
from app.models.user_behavior import UserBehavior
from app.models.user_favorite import UserFavorite
from app.models.user_subscription import UserSubscription

__all__ = ["Opportunity", "User", "UserBehavior", "UserFavorite", "UserSubscription"]
