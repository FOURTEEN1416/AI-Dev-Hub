"""
收藏（Favorites）API 路由
提供用户收藏的增删查接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.user import UserFavoriteListResponse
from app.services.favorite import FavoriteService

router = APIRouter(prefix="/favorites", tags=["用户收藏"])


@router.get("", response_model=UserFavoriteListResponse, summary="获取用户收藏列表")
async def get_favorites(
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserFavoriteListResponse:
    """
    获取当前用户的收藏列表（含机会详情）

    - **page**: 页码，从 1 开始
    - **limit**: 每页数量，最大 100
    """
    favorite_service = FavoriteService(db)
    items, total = await favorite_service.get_user_favorites(
        user_id=current_user.id,
        page=page,
        limit=limit,
    )

    return UserFavoriteListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
    )


@router.post("", status_code=status.HTTP_201_CREATED, summary="添加收藏")
async def add_favorite(
    opportunity_id: int = Query(..., description="机会ID"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    添加收藏

    - **opportunity_id**: 要收藏的机会ID
    """
    favorite_service = FavoriteService(db)

    # 检查机会是否存在
    if not await favorite_service.check_opportunity_exists(opportunity_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"机会不存在，ID: {opportunity_id}",
        )

    # 检查是否已收藏
    if await favorite_service.is_favorited(current_user.id, opportunity_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已收藏过该机会",
        )

    # 添加收藏
    favorite = await favorite_service.add_favorite(current_user.id, opportunity_id)

    return {
        "message": "收藏成功",
        "data": {
            "favorite_id": favorite.id,
            "opportunity_id": opportunity_id,
        },
    }


@router.delete("/{opportunity_id}", summary="取消收藏")
async def remove_favorite(
    opportunity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    取消收藏

    - **opportunity_id**: 要取消收藏的机会ID
    """
    favorite_service = FavoriteService(db)

    # 取消收藏
    success = await favorite_service.remove_favorite(current_user.id, opportunity_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到该收藏记录",
        )

    return {"message": "取消收藏成功"}


@router.get("/check/{opportunity_id}", summary="检查是否已收藏")
async def check_favorite(
    opportunity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    检查当前用户是否已收藏某个机会

    - **opportunity_id**: 机会ID
    """
    favorite_service = FavoriteService(db)

    is_favorited = await favorite_service.is_favorited(current_user.id, opportunity_id)

    return {
        "opportunity_id": opportunity_id,
        "is_favorited": is_favorited,
    }
