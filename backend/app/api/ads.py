from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import math 

from app.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.ad import Ad, AdCategory, AdLevel, AdFormat
from app.schemas.ad import AdCreate, AdUpdate, AdOut, AdListOut, AdFilter
from app.services.ad import AdService

router = APIRouter(prefix="/ads", tags=["Ads"])

@router.post("", response_model=AdOut, status_code=status.HTTP_201_CREATED)
async def create_ad(
    ad_data: AdCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Создание нового объявления."""
    ad_service = AdService(db)
    
    try:
        ad = await ad_service.create_ad(ad_data, str(current_user.id))
        return ad
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{ad_id}", response_model=AdOut)
async def get_ad(
    ad_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Получение объявления по ID."""
    ad_service = AdService(db)
    ad = await ad_service.get_ad_by_id(ad_id)
    
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )
    
    return ad

@router.patch("/{ad_id}", response_model=AdOut)
async def update_ad(
    ad_id: str,
    update_data: AdUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновление объявления."""
    ad_service = AdService(db)
    
    ad = await ad_service.get_ad_by_id(ad_id)
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )
    
    if ad.author_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot edit other user's ad"
        )
    
    updated_ad = await ad_service.update_ad(ad, update_data)
    return updated_ad

@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad(
    ad_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Полноценное удаление объявления."""
    ad_service = AdService(db)

    ad = await ad_service.get_ad_by_id(ad_id)
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ad not found"
        )
    
    if ad.author_id != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete other user's ad"
        )
    
    await ad_service.delete_ad(ad)
    return None

@router.get("", response_model=AdListOut)
async def get_ads(
    category: Optional[AdCategory] = Query(None),
    level: Optional[AdLevel] = Query(None),
    format: Optional[AdFormat] = Query(None),
    q: Optional[str] = Query(None),
    sort: str = Query("newest", regex="^(newest|popular)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Получение ленты объявлений с фильтрами и пагинацией."""
    filters = AdFilter(
        category=category,
        level=level,
        format=format,
        q=q,
        sort=sort,
        page=page,
        page_size=page_size
    )
    
    ad_service = AdService(db)
    ads, total = await ad_service.get_ads_with_filters(filters)

    pages = math.ceil(total / page_size) if total > 0 else 1
    
    return AdListOut(
        items=ads,
        total=total,
        page=page,
        pages=pages
    )

@router.get("/my/ads", response_model=list[AdOut])
async def get_my_ads(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение всех объявлений текущего пользователя."""
    ad_service = AdService(db)
    ads = await ad_service.get_user_ads(str(current_user.id))
    return ads