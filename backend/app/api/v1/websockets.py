from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List
import json
from app.api.deps import get_current_user
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()

class AlertNotifier:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_alert(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

notifier = AlertNotifier()

@router.websocket("/alerts")
async def websocket_alerts(websocket: WebSocket, token: str):
    # Extremely basic auth for WS
    from app.core.security import decode_access_token
    db = next(get_db())
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=1008)
        return
        
    await notifier.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        notifier.disconnect(websocket)
