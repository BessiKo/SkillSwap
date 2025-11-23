from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class ChatBase(BaseModel):
    ad_id: str  
    user2_id: str 


class ChatCreate(ChatBase):
    pass


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    ad_id: str  
    user1_id: str  
    user2_id: str  
    created_at: datetime
    last_message: Optional["MessageResponse"] = None
    unread_count: int = 0


class MessageBase(BaseModel):
    text: str


class MessageCreate(MessageBase):
    chat_id: int


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    chat_id: int
    sender_id: str  
    text: str
    created_at: datetime
    read_at: Optional[datetime] = None
    sender_name: str


class WebSocketMessage(BaseModel):
    type: str 
    chat_id: int
    sender_id: str 
    data: dict 


ChatResponse.model_rebuild()