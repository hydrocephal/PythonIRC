from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services import chat as chat_service

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    try:
        websocket_user = await chat_service.websocket_connection_logic(websocket, token, db)
        if websocket_user is None:
            await websocket.close(code=4003) #Forbidden
            return
    except (RuntimeError, WebSocketDisconnect):
        pass
 