from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
import enum


class DealStatus(str, enum.Enum):
    """Статусы сделки"""
    NEW = "new"  
    DISCUSSION = "discussion"  
    CONFIRMED = "confirmed"  
    COMPLETED = "completed"  
    CANCELED = "canceled"  


class Deal(Base):
    """Модель сделки"""
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), unique=True, nullable=False)
    status = Column(Enum(DealStatus), default=DealStatus.NEW, nullable=False)

    student_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False) 
    teacher_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  

    proposed_skill = Column(String(200), nullable=True) 
    proposed_time = Column(String(100), nullable=True)   
    proposed_place = Column(String(200), nullable=True)  
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    chat = relationship("Chat", back_populates="deal")
    student = relationship("User", foreign_keys=[student_id])
    teacher = relationship("User", foreign_keys=[teacher_id])
    status_logs = relationship("DealStatusLog", back_populates="deal", cascade="all, delete-orphan")


class DealStatusLog(Base):
    """Логи изменений статуса сделки"""
    __tablename__ = "deal_status_logs"

    id = Column(Integer, primary_key=True, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id", ondelete="CASCADE"), nullable=False)
    old_status = Column(Enum(DealStatus), nullable=True)
    new_status = Column(Enum(DealStatus), nullable=False)
    changed_by_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reason = Column(Text, nullable=True)  
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    deal = relationship("Deal", back_populates="status_logs")
    changed_by = relationship("User")