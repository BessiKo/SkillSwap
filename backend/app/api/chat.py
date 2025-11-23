from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import json

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.chat import ChatResponse, MessageResponse, MessageCreate
from app.services.chat import ChatService
from app.websocket.manager import manager

router = APIRouter()

router = APIRouter(prefix="/chats", tags=["Chats"]) 

@router.post("/ads/{ad_id}/respond", response_model=ChatResponse)
async def respond_to_ad(
    ad_id: str,  
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Откликнуться на объявление (создает чат)"""
    chat_service = ChatService(db)
    
    chat_data = {"ad_id": ad_id, "user2_id": current_user.id}
    chat = await chat_service.create_chat(chat_data, current_user.id)
    
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create chat"
        )
    
    return chat


@router.get("/chats", response_model=List[ChatResponse])
async def get_my_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить мои чаты"""
    chat_service = ChatService(db)
    chats = await chat_service.get_user_chats(current_user.id)
    
    response_chats = []
    for chat in chats:
        chat_dict = {
            "id": chat.id,
            "ad_id": chat.ad_id,
            "user1_id": chat.user1_id,
            "user2_id": chat.user2_id,
            "created_at": chat.created_at,
            "last_message": None,  
            "unread_count": 0      
        }
        response_chats.append(ChatResponse(**chat_dict))
    
    return response_chats


@router.get("/chats/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить сообщения чата"""
    chat_service = ChatService(db)
    messages = await chat_service.get_chat_messages(chat_id, current_user.id, limit, offset)

    response_messages = []
    for message in messages:
        message_dict = {
            "id": message.id,
            "chat_id": message.chat_id,
            "sender_id": message.sender_id,
            "text": message.text,
            "created_at": message.created_at,
            "read_at": message.read_at,
            "sender_name": f"{message.sender.first_name} {message.sender.last_name}"
        }
        response_messages.append(MessageResponse(**message_dict))
    
    return response_messages


@router.websocket("/ws/chat/{chat_id}")
async def websocket_chat(
    websocket: WebSocket,
    chat_id: int,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """WebSocket endpoint для чата"""
    from app.utils.security import decode_token

    token_payload = decode_token(token)
    if not token_payload:
        await websocket.close(code=1008)
        return
    
    user_id = token_payload.get("sub")
    if not user_id:
        await websocket.close(code=1008)
        return

    chat_service = ChatService(db)
    chat = await chat_service.get_chat(chat_id, user_id)
    if not chat:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, chat_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "message":

                new_message = await chat_service.create_message(
                    MessageCreate(
                        chat_id=chat_id,
                        text=message_data["data"]["text"]
                    ),
                    user_id
                )
                
                if new_message:

                    response_message = {
                        "type": "message",
                        "data": {
                            "id": new_message.id,
                            "chat_id": new_message.chat_id,
                            "sender_id": new_message.sender_id,
                            "sender_name": f"{new_message.sender.first_name} {new_message.sender.last_name}",
                            "text": new_message.text,
                            "created_at": new_message.created_at.isoformat(),
                            "read_at": new_message.read_at.isoformat() if new_message.read_at else None
                        }
                    }
                    await manager.broadcast_to_chat(
                        json.dumps(response_message),
                        chat_id,
                        websocket
                    )
            
            elif message_data["type"] == "typing":
                await manager.send_user_typing(
                    chat_id,
                    user_id,
                    message_data["data"]["is_typing"]
                )
            
            elif message_data["type"] == "read_receipt":

                await chat_service.mark_messages_as_read(chat_id, user_id)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_id, user_id)