from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.models.deal import DealStatus


class DealBase(BaseModel):
    proposed_skill: Optional[str] = None
    proposed_time: Optional[str] = None
    proposed_place: Optional[str] = None


class DealCreate(DealBase):
    chat_id: int


class DealUpdate(BaseModel):
    status: Optional[DealStatus] = None
    proposed_skill: Optional[str] = None
    proposed_time: Optional[str] = None
    proposed_place: Optional[str] = None


class DealStatusLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    old_status: Optional[DealStatus] = None
    new_status: DealStatus
    changed_by_id: str
    reason: Optional[str] = None
    created_at: datetime
    changed_by_name: str


class DealOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    chat_id: int
    status: DealStatus
    student_id: str
    teacher_id: str
    proposed_skill: Optional[str] = None
    proposed_time: Optional[str] = None
    proposed_place: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    status_logs: List[DealStatusLogOut] = []
    student_name: str = ""
    teacher_name: str = ""


class DealStatusUpdate(BaseModel):
    status: DealStatus
    reason: Optional[str] = None


class DealProposal(BaseModel):
    """Схема для предложения условий сделки"""
    skill: str
    time: str
    place: str


class WebSocketDealMessage(BaseModel):
    type: str 
    chat_id: int
    user_id: str
    data: dict