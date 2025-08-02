from fastapi import WebSocket
from typing import Dict, List

class WebSocketManager:
    """
    Manages WebSocket connections for real-time project synchronization.
    """
    def __init__(self):
        # A dictionary to hold active connections, mapping project_id to a list of WebSockets.
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, project_id: str):
        """
        Accepts a new WebSocket connection and adds it to the list for a project.
        """
        await websocket.accept()
        if project_id not in self.active_connections:
            self.active_connections[project_id] = []
        self.active_connections[project_id].append(websocket)

    def disconnect(self, websocket: WebSocket, project_id: str):
        """
        Removes a WebSocket connection from the list for a project.
        """
        if project_id in self.active_connections:
            self.active_connections[project_id].remove(websocket)
            # Clean up the project_id key if no connections are left
            if not self.active_connections[project_id]:
                del self.active_connections[project_id]

    async def broadcast_to_project(self, project_id: str, message: str):
        """
        Broadcasts a message to all connected clients for a specific project.
        """
        if project_id in self.active_connections:
            for connection in self.active_connections[project_id]:
                await connection.send_text(message)

# Create a single instance of the manager to be used across the application
manager = WebSocketManager()
