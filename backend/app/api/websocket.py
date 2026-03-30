"""
WebSocket endpoints for real-time updates.
"""
import asyncio
import json
from typing import Dict, List, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings

router = APIRouter(tags=["websocket"])

# Active WebSocket connections
active_connections: Set[WebSocket] = set()


class ConnectionManager:
    """Manage WebSocket connections."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """Accept and track new connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove connection."""
        self.active_connections.discard(websocket)
        print(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: Dict):
        """Broadcast message to all connected clients."""
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.active_connections.discard(conn)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.

    Events:
    - flow_update: New flow detected
    - classification_result: Classification completed
    - alert: Security alert
    - stats_update: Statistics update
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle client messages
            msg_type = message.get("type")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            elif msg_type == "subscribe":
                channel = message.get("channel", "all")
                await websocket.send_json({
                    "type": "subscribed",
                    "channel": channel
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_flow_update(flow_data: Dict):
    """Broadcast new flow to all clients."""
    await manager.broadcast({
        "type": "flow_update",
        "data": flow_data
    })


async def broadcast_classification(flow_id: int, category: str, confidence: float):
    """Broadcast classification result."""
    await manager.broadcast({
        "type": "classification_result",
        "data": {
            "flow_id": flow_id,
            "category": category,
            "confidence": round(confidence, 4)
        }
    })


async def broadcast_alert(alert_type: str, message: str, severity: str = "warning"):
    """Broadcast security alert."""
    await manager.broadcast({
        "type": "alert",
        "data": {
            "type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": asyncio.get_event_loop().time()
        }
    })


async def broadcast_stats(stats: Dict):
    """Broadcast statistics update."""
    await manager.broadcast({
        "type": "stats_update",
        "data": stats
    })
