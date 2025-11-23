from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select, func, and_, or_
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.deal import Deal, DealStatusLog
from app.schemas.deal import (
    DealOut, DealCreate, DealUpdate, DealStatusUpdate, 
    DealProposal, DealStatusLogOut
)
from app.services.deal import DealService
from app.websocket.manager import manager

router = APIRouter(prefix="/deals", tags=["Deals"])


@router.post("/chats/{chat_id}/propose", response_model=DealOut)
async def propose_deal(
    chat_id: int,
    proposal: DealProposal,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Предложить условия сделки"""
    deal_service = DealService(db)
    
    deal_data = DealCreate(
        chat_id=chat_id,
        proposed_skill=proposal.skill,
        proposed_time=proposal.time,
        proposed_place=proposal.place
    )
    
    deal = await deal_service.create_deal(deal_data, str(current_user.id))
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create deal"
        )

    updated_deal = await deal_service.propose_deal_terms(deal, proposal, str(current_user.id))
    if not updated_deal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot propose deal terms"
        )
    
    return _enrich_deal_response(updated_deal)


@router.patch("/chats/{chat_id}/status", response_model=DealOut)
async def update_deal_status(
    chat_id: int,
    status_update: DealStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить статус сделки"""
    deal_service = DealService(db)
    
    deal = await deal_service.get_deal_by_chat_id(chat_id)
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    if str(current_user.id) not in [deal.student_id, deal.teacher_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant of this deal"
        )
    
    updated_deal = await deal_service.update_deal_status(deal, status_update, str(current_user.id))
    if not updated_deal:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status transition"
        )

    await _broadcast_deal_update(chat_id, updated_deal, str(current_user.id))
    
    return _enrich_deal_response(updated_deal)


@router.get("/chats/{chat_id}", response_model=DealOut)
async def get_chat_deal(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить сделку по ID чата"""
    deal_service = DealService(db)
    
    deal = await deal_service.get_deal_by_chat_id(chat_id)
    if not deal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )
    
    if str(current_user.id) not in [deal.student_id, deal.teacher_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a participant of this deal"
        )
    
    return _enrich_deal_response(deal)


@router.get("/my", response_model=List[DealOut])
async def get_my_deals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить все мои сделки"""
    deal_service = DealService(db)
    
    deals = await deal_service.get_user_deals(str(current_user.id))
    
    return [_enrich_deal_response(deal) for deal in deals]


@router.get("/{deal_id}/logs", response_model=List[DealStatusLogOut])
async def get_deal_logs(
    deal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить логи сделки"""
    from sqlalchemy.orm import selectinload
    from app.models.deal import Deal, DealStatusLog

    result = await db.execute(
        select(Deal).where(Deal.id == deal_id)
    )
    deal = result.scalar_one_or_none()
    
    if not deal or str(current_user.id) not in [deal.student_id, deal.teacher_id]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deal not found"
        )

    result = await db.execute(
        select(DealStatusLog)
        .options(selectinload(DealStatusLog.changed_by))
        .where(DealStatusLog.deal_id == deal_id)
        .order_by(DealStatusLog.created_at.asc())
    )
    logs = result.scalars().all()

    enriched_logs = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "old_status": log.old_status,
            "new_status": log.new_status,
            "changed_by_id": log.changed_by_id,
            "reason": log.reason,
            "created_at": log.created_at,
            "changed_by_name": f"{log.changed_by.first_name} {log.changed_by.last_name}"
        }
        enriched_logs.append(DealStatusLogOut(**log_dict))
    
    return enriched_logs


def _enrich_deal_response(deal: Deal) -> dict:
    """Обогащает ответ данными о пользователях"""
    return {
        "id": deal.id,
        "chat_id": deal.chat_id,
        "status": deal.status,
        "student_id": deal.student_id,
        "teacher_id": deal.teacher_id,
        "proposed_skill": deal.proposed_skill,
        "proposed_time": deal.proposed_time,
        "proposed_place": deal.proposed_place,
        "created_at": deal.created_at,
        "updated_at": deal.updated_at,
        "status_logs": [
            {
                "id": log.id,
                "old_status": log.old_status,
                "new_status": log.new_status,
                "changed_by_id": log.changed_by_id,
                "reason": log.reason,
                "created_at": log.created_at,
                "changed_by_name": f"{log.changed_by.first_name} {log.changed_by.last_name}"
            } for log in deal.status_logs
        ],
        "student_name": f"{deal.student.first_name} {deal.student.last_name}",
        "teacher_name": f"{deal.teacher.first_name} {deal.teacher.last_name}"
    }


async def _broadcast_deal_update(chat_id: int, deal: Deal, user_id: str):
    """Отправить обновление сделки через WebSocket"""
    from app.websocket.manager import manager
    import json
    
    deal_response = _enrich_deal_response(deal)

    await manager.send_deal_update(chat_id, deal_response)

    if deal.status_logs:
        last_log = deal.status_logs[-1]
        await manager.send_deal_status_change(
            chat_id=chat_id,
            old_status=last_log.old_status.value if last_log.old_status else None,
            new_status=last_log.new_status.value,
            user_id=user_id,
            reason=last_log.reason
        )