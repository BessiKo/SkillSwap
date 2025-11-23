from typing import Dict, Set
from fastapi import WebSocket
import json
import datetime


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.user_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: int, user_id: int):
        await websocket.accept()
        
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = set()
        self.active_connections[chat_id].add(websocket)
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)

    def disconnect(self, websocket: WebSocket, chat_id: int, user_id: int):
        if chat_id in self.active_connections:
            self.active_connections[chat_id].discard(websocket)
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]
        
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_chat(self, message: str, chat_id: int, exclude_websocket: WebSocket = None):
        if chat_id in self.active_connections:
            for connection in self.active_connections[chat_id]:
                if connection != exclude_websocket:
                    try:
                        await connection.send_text(message)
                    except Exception:
                        self.disconnect(connection, chat_id, self._get_user_id_by_connection(connection))

    async def send_user_typing(self, chat_id: int, user_id: int, is_typing: bool):
        message = {
            "type": "typing",
            "chat_id": chat_id,
            "user_id": user_id,
            "is_typing": is_typing
        }
        await self.broadcast_to_chat(json.dumps(message), chat_id)

    async def send_deal_update(self, chat_id: int, deal_data: dict):
        message = {
            "type": "deal_update",
            "data": deal_data
        }
        await self.broadcast_to_chat(json.dumps(message), chat_id)

    async def send_deal_proposal(self, chat_id: int, proposal_data: dict, user_id: int):
        message = {
            "type": "deal_proposal", 
            "chat_id": chat_id,
            "user_id": user_id,
            "data": proposal_data
        }
        await self.broadcast_to_chat(json.dumps(message), chat_id)

    async def send_deal_status_change(self, chat_id: int, old_status: str, new_status: str, user_id: int, reason: str = None):
        message = {
            "type": "deal_status_change",
            "chat_id": chat_id,
            "user_id": user_id,
            "data": {
                "old_status": old_status,
                "new_status": new_status,
                "reason": reason,
                "timestamp": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            }
        }
        await self.broadcast_to_chat(json.dumps(message), chat_id)

    def _get_user_id_by_connection(self, websocket: WebSocket) -> int:
        for user_id, connections in self.user_connections.items():
            if websocket in connections:
                return user_id
        return None


manager = ConnectionManager()