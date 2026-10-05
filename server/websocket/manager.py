"""
server/websocket/manager.py
===========================
WebSocket connection manager for real-time live render streaming and interactive console updates.
"""
from fastapi import WebSocket
from typing import Dict, List


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, reel_id: str, websocket: WebSocket):
        await websocket.accept()
        if reel_id not in self.active_connections:
            self.active_connections[reel_id] = []
        self.active_connections[reel_id].append(websocket)

    def disconnect(self, reel_id: str, websocket: WebSocket):
        if reel_id in self.active_connections:
            if websocket in self.active_connections[reel_id]:
                self.active_connections[reel_id].remove(websocket)

    async def broadcast_to_reel(self, reel_id: str, message: dict):
        if reel_id in self.active_connections:
            for connection in self.active_connections[reel_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass


ws_manager = ConnectionManager()
