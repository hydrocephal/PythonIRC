import asyncio
import json
from datetime import datetime, timezone

from fastapi import WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import SessionLocal
from app.models.models import Message, User


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[tuple[WebSocket, int, str]] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: int, username: str):
        async with self._lock:
            self.active_connections.append((websocket, user_id, username))
        await self.broadcast({"type": "system", "content": f"{username} joined the chat."})

    async def disconnect(self, websocket: WebSocket):                                                 #add logs with usernames
        async with self._lock:
            self.active_connections = [c for c in self.active_connections if c[0] != websocket]

    async def broadcast(self, message: dict):
        async def send_or_mark_dead(connection):
            try:
                await connection[0].send_json(message)
                return None
            except Exception:
                return connection
        
        async with self._lock:
            connections = self.active_connections.copy()

        results = await asyncio.gather(*[send_or_mark_dead(c) for c in connections])
        dead = [c for c in results if c is not None]
        
        if dead:
            async with self._lock:
                for connection in dead:
                    if connection in self.active_connections:
                        self.active_connections.remove(connection)

    def get_online_users(self):
        return [c[2] for c in self.active_connections]

manager = ConnectionManager()

async def get_user_from_token(token: str, db: AsyncSession):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    result = await db.execute(select(User).where(User.username == username))           
    return result.scalar_one_or_none()

async def websocket_connection_logic(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()    
    token = json.loads(data).get("token")    
    if not token:
        return None
    
    async with SessionLocal() as session:
        user = await get_user_from_token(token, session)        
        if user is None:
            return None
    
    await manager.connect(websocket, user.id, user.username)    
    
    try:
        async with SessionLocal() as session:            
            last_messages = await session.execute(select(Message).options(
                joinedload(Message.sender)).order_by(Message.timestamp.desc()).limit(50))
                            
            for msg in reversed(last_messages.unique().scalars().all()):
                sender_name = msg.sender.username if msg.sender else "Unknown"
                await websocket.send_json({
                    "type": "message",
                    "username": sender_name,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                })
            
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get("command") == "online":
                online_users = manager.get_online_users()
                await websocket.send_json({
                    "type": "system",
                    "content": f"Online users: {', '.join(online_users)}"
                })
                continue
            content = message_data.get("content")
            if content:
                async with SessionLocal() as session:
                    try:
                        new_msg = Message(user_id=user.id, content=content)
                        session.add(new_msg)
                        await session.commit()
            
                        await manager.broadcast({
                            "type": "message",
                            "username": user.username,
                            "content": content,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                    except Exception:
                        await session.rollback()

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        await manager.broadcast({"type": "system", "content": f"{user.username} left the chat."})
    except RuntimeError:
        await manager.disconnect(websocket)