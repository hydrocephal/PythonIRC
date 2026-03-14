from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session, joinedload
from app.models.models import User, Message
from app.core.config import settings
from app.db.database import SessionLocal
from jose import JWTError, jwt
from datetime import datetime
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[tuple[WebSocket, int, str]] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: int, username: str):
        async with self._lock:
            await websocket.accept()
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
        
        results = await asyncio.gather(*[send_or_mark_dead(c) for c in self.active_connections])
        dead = [c for c in results if c is not None]
        for connection in dead:
            self.active_connections.remove(connection)

    def get_online_users(self):
        return [c[2] for c in self.active_connections]

manager = ConnectionManager()

async def get_user_from_token(token: str, db: Session):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None

    return db.query(User).filter(User.username == username).first()

async def websocket_connection_logic(websocket: WebSocket, token: str, db: Session):
    user = await get_user_from_token(token, db)
    if user is None:
        return None
    
    await manager.connect(websocket, user.id, user.username)

    try:
        last_messages = db.query(Message).options(
            joinedload(Message.sender)).order_by(Message.timestamp.desc()).limit(50).all()
        for msg in reversed(last_messages):
            db.close()
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
                with SessionLocal() as session:
                    new_msg = Message(user_id=user.id, content=content)
                    session.add(new_msg)
                    session.commit()

                await manager.broadcast({
                    "type": "message",
                    "username": user.username,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                })

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        await manager.broadcast({"type": "system", "content": f"{user.username} left the chat"})
    except RuntimeError:
        await manager.disconnect(websocket)