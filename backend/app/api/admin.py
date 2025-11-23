from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import math

from app.database import get_db
from app.api.deps import get_admin_user
from app.models.user import User, UserRole
from app.models.admin import AdminActionType
from app.models.deal import DealStatus
from app.schemas.admin import (
    UserListOut, AdListAdminOut, AdminLogOut, AdminStatsOut,
    ChatAdminOut, DealAdminOut, MessageAdminOut,
    UserBanRequest, AdminActionRequest
)
from app.services.admin import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])

# --- Пользователи ---

@router.get("/users", response_model=dict)
async def get_users_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка пользователей для админ-панели."""
    admin_service = AdminService(db)
    users, total = await admin_service.get_users_list(
        page=page,
        page_size=page_size,
        search=search,
        role=role,
        is_active=is_active
    )
    
    users_out = []
    for user in users:
        user_dict = {
            "id": user.id,
            "phone": user.phone,
            "role": user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "profile": user.profile
        }
        users_out.append(UserListOut(**user_dict))
    
    pages = math.ceil(total / page_size) if total > 0 else 1
    
    return {
        "items": users_out,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.post("/users/{user_id}/ban", response_model=dict)
async def ban_user(
    user_id: str,
    ban_data: UserBanRequest,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Блокировка пользователя."""
    admin_service = AdminService(db)
    
    try:
        user = await admin_service.ban_user(user_id, str(current_user.id), ban_data)
        return {
            "message": "User banned successfully",
            "user_id": user.id,
            "is_active": user.is_active
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/users/{user_id}/unban", response_model=dict)
async def unban_user(
    user_id: str,
    unban_data: AdminActionRequest,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Разблокировка пользователя."""
    admin_service = AdminService(db)
    
    try:
        user = await admin_service.unban_user(user_id, str(current_user.id), unban_data)
        return {
            "message": "User unbanned successfully",
            "user_id": user.id,
            "is_active": user.is_active
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# --- Объявления ---

@router.get("/ads", response_model=dict)
async def get_ads_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    author_id: Optional[str] = Query(None),
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка объявлений для админ-панели."""
    admin_service = AdminService(db)
    ads, total = await admin_service.get_ads_list(
        page=page,
        page_size=page_size,
        search=search,
        category=category,
        author_id=author_id
    )
    
    pages = math.ceil(total / page_size) if total > 0 else 1
    
    return {
        "items": ads,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.delete("/ads/{ad_id}", status_code=status.HTTP_200_OK)
async def delete_ad_admin(
    ad_id: str,
    delete_data: AdminActionRequest,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Удаление объявления администратором."""
    admin_service = AdminService(db)
    
    try:
        await admin_service.delete_ad(ad_id, str(current_user.id), delete_data)
        return {"message": "Ad deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# --- Чаты ---

@router.get("/chats", response_model=dict)
async def get_chats_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    ad_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка чатов для админ-панели."""
    admin_service = AdminService(db)
    chats, total = await admin_service.get_chats_list(
        page=page,
        page_size=page_size,
        ad_id=ad_id,
        user_id=user_id
    )
    
    pages = math.ceil(total / page_size) if total > 0 else 1
    
    return {
        "items": chats,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.get("/chats/{chat_id}/messages", response_model=List[MessageAdminOut])
async def get_chat_messages(
    chat_id: int,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение сообщений чата."""
    admin_service = AdminService(db)
    messages = await admin_service.get_chat_messages(chat_id)
    return messages

@router.delete("/chats/{chat_id}", status_code=status.HTTP_200_OK)
async def delete_chat_admin(
    chat_id: int,
    delete_data: AdminActionRequest,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Удаление чата администратором."""
    admin_service = AdminService(db)
    
    try:
        await admin_service.delete_chat(chat_id, str(current_user.id), delete_data)
        return {"message": "Chat deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# --- Сделки ---

@router.get("/deals", response_model=dict)
async def get_deals_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[DealStatus] = Query(None),
    user_id: Optional[str] = Query(None),
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка сделок для админ-панели."""
    admin_service = AdminService(db)
    deals, total = await admin_service.get_deals_list(
        page=page,
        page_size=page_size,
        status=status,
        user_id=user_id
    )
    
    pages = math.ceil(total / page_size) if total > 0 else 1
    
    return {
        "items": deals,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.post("/deals/{deal_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_deal_admin(
    deal_id: int,
    cancel_data: AdminActionRequest,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Отмена сделки администратором."""
    admin_service = AdminService(db)
    
    try:
        deal = await admin_service.cancel_deal(deal_id, str(current_user.id), cancel_data)
        return {
            "message": "Deal cancelled successfully",
            "deal_id": deal.id,
            "status": deal.status.value
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# --- Логи и статистика ---

@router.get("/logs", response_model=dict)
async def get_admin_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    action_type: Optional[AdminActionType] = Query(None),
    admin_id: Optional[str] = Query(None),
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение логов административных действий."""
    admin_service = AdminService(db)
    logs, total = await admin_service.get_admin_logs(
        page=page,
        page_size=page_size,
        action_type=action_type,
        admin_id=admin_id
    )
    
    pages = math.ceil(total / page_size) if total > 0 else 1
    
    return {
        "items": logs,
        "total": total,
        "page": page,
        "pages": pages
    }

@router.get("/stats", response_model=AdminStatsOut)
async def get_admin_stats(
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Получение статистики для админ-панели."""
    admin_service = AdminService(db)
    stats = await admin_service.get_admin_stats()
    return AdminStatsOut(**stats)