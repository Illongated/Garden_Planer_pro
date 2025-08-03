import json
import logging
from datetime import datetime
from typing import Dict, Set, Any, Optional
from collections import defaultdict
from fastapi import WebSocket
import uuid

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Enhanced WebSocket manager for real-time collaboration."""
    
    def __init__(self):
        # Agronomic connections (existing)
        self.active_connections: Dict[str, WebSocket] = {}
        self.garden_subscriptions: Dict[str, Set[str]] = defaultdict(set)
        self.user_gardens: Dict[str, Set[str]] = defaultdict(set)
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Project collaboration connections (new)
        self.project_connections: Dict[str, Dict[str, WebSocket]] = defaultdict(dict)
        self.user_projects: Dict[str, Set[str]] = defaultdict(set)
        self.project_users: Dict[str, Set[str]] = defaultdict(set)
        self.cursor_positions: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
        
        # Connection health tracking
        self.connection_heartbeats: Dict[str, datetime] = {}
        self.last_activity: Dict[str, datetime] = {}
    
    # --- Agronomic WebSocket Methods (existing) ---
    
    def add_connection(self, user_id: str, websocket: WebSocket):
        """Add a new agronomic connection."""
        self.active_connections[user_id] = websocket
        self.connection_metadata[user_id] = {
            "connected_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }
        logger.info(f"Agronomic connection added for user {user_id}")
    
    def remove_connection(self, user_id: str):
        """Remove an agronomic connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.connection_metadata:
            del self.connection_metadata[user_id]
        
        # Remove from garden subscriptions
        for garden_id in self.user_gardens.get(user_id, set()):
            self.garden_subscriptions[garden_id].discard(user_id)
            if not self.garden_subscriptions[garden_id]:
                del self.garden_subscriptions[garden_id]
        
        if user_id in self.user_gardens:
            del self.user_gardens[user_id]
        
        logger.info(f"Agronomic connection removed for user {user_id}")
    
    def subscribe_to_garden(self, user_id: str, garden_id: str):
        """Subscribe user to garden updates."""
        self.user_gardens[user_id].add(garden_id)
        self.garden_subscriptions[garden_id].add(user_id)
        logger.info(f"User {user_id} subscribed to garden {garden_id}")
    
    def unsubscribe_from_garden(self, user_id: str, garden_id: str):
        """Unsubscribe user from garden updates."""
        self.user_gardens[user_id].discard(garden_id)
        self.garden_subscriptions[garden_id].discard(user_id)
        if not self.garden_subscriptions[garden_id]:
            del self.garden_subscriptions[garden_id]
        logger.info(f"User {user_id} unsubscribed from garden {garden_id}")
    
    async def broadcast_to_garden(self, garden_id: str, message: Dict[str, Any]):
        """Broadcast message to all users subscribed to a garden."""
        if garden_id not in self.garden_subscriptions:
            logger.warning(f"No subscribers for garden {garden_id}")
            return
        
        subscribers = self.garden_subscriptions[garden_id].copy()
        failed_sends = []
        
        for user_id in subscribers:
            try:
                await self.send_to_user(user_id, message)
            except Exception as e:
                logger.error(f"Failed to send message to user {user_id}: {str(e)}")
                failed_sends.append(user_id)
        
        # Clean up failed connections
        for user_id in failed_sends:
            self.remove_connection(user_id)
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any]):
        """Send message to a specific user."""
        if user_id not in self.active_connections:
            logger.warning(f"No active connection for user {user_id}")
            return
        
        try:
            websocket = self.active_connections[user_id]
            await websocket.send_text(json.dumps(message))
            self.last_activity[user_id] = datetime.utcnow()
        except Exception as e:
            logger.error(f"Failed to send message to user {user_id}: {str(e)}")
            raise
    
    # --- Project Collaboration Methods (new) ---
    
    def add_project_connection(self, project_id: str, user_id: str, websocket: WebSocket):
        """Add a new project collaboration connection."""
        self.project_connections[project_id][user_id] = websocket
        self.user_projects[user_id].add(project_id)
        self.project_users[project_id].add(user_id)
        
        # Initialize cursor position for user
        self.cursor_positions[project_id][user_id] = {
            "x": 0,
            "y": 0,
            "last_update": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Project connection added for user {user_id} to project {project_id}")
    
    def remove_project_connection(self, project_id: str, user_id: str):
        """Remove a project collaboration connection."""
        if project_id in self.project_connections:
            self.project_connections[project_id].pop(user_id, None)
            if not self.project_connections[project_id]:
                del self.project_connections[project_id]
        
        self.user_projects[user_id].discard(project_id)
        self.project_users[project_id].discard(user_id)
        
        # Remove cursor position
        if project_id in self.cursor_positions:
            self.cursor_positions[project_id].pop(user_id, None)
            if not self.cursor_positions[project_id]:
                del self.cursor_positions[project_id]
        
        logger.info(f"Project connection removed for user {user_id} from project {project_id}")
    
    async def broadcast_to_project(
        self, 
        project_id: str, 
        message: Dict[str, Any], 
        exclude_user_id: Optional[str] = None
    ):
        """Broadcast message to all users in a project."""
        if project_id not in self.project_connections:
            logger.warning(f"No connections for project {project_id}")
            return
        
        connections = self.project_connections[project_id].copy()
        failed_sends = []
        
        for user_id, websocket in connections.items():
            if exclude_user_id and user_id == exclude_user_id:
                continue
            
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send project message to user {user_id}: {str(e)}")
                failed_sends.append(user_id)
        
        # Clean up failed connections
        for user_id in failed_sends:
            self.remove_project_connection(project_id, user_id)
    
    async def broadcast_to_user(self, user_id: str, message: Dict[str, Any]):
        """Broadcast message to a specific user (for project notifications)."""
        # Try project connections first
        for project_id, connections in self.project_connections.items():
            if user_id in connections:
                try:
                    websocket = connections[user_id]
                    await websocket.send_text(json.dumps(message))
                    return
                except Exception as e:
                    logger.error(f"Failed to send project message to user {user_id}: {str(e)}")
                    self.remove_project_connection(project_id, user_id)
        
        # Fall back to agronomic connections
        await self.send_to_user(user_id, message)
    
    def update_cursor_position(self, project_id: str, user_id: str, x: float, y: float):
        """Update cursor position for a user in a project."""
        if project_id not in self.cursor_positions:
            self.cursor_positions[project_id] = {}
        
        self.cursor_positions[project_id][user_id] = {
            "x": x,
            "y": y,
            "last_update": datetime.utcnow().isoformat()
        }
    
    def get_project_cursors(self, project_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all cursor positions for a project."""
        return self.cursor_positions.get(project_id, {})
    
    def get_project_users(self, project_id: str) -> Set[str]:
        """Get all users currently connected to a project."""
        return self.project_users.get(project_id, set())
    
    def get_user_projects(self, user_id: str) -> Set[str]:
        """Get all projects a user is currently connected to."""
        return self.user_projects.get(user_id, set())
    
    # --- Token Validation (simplified) ---
    
    def validate_token(self, token: str) -> Optional[str]:
        """Validate user token and return user ID."""
        # This is a simplified implementation
        # In production, you'd validate the JWT token properly
        try:
            # For demo purposes, assume token is user_id
            # In real implementation, decode JWT and extract user_id
            return token
        except Exception as e:
            logger.error(f"Token validation failed: {str(e)}")
            return None
    
    # --- Health Monitoring ---
    
    def update_heartbeat(self, user_id: str):
        """Update heartbeat for a user connection."""
        self.connection_heartbeats[user_id] = datetime.utcnow()
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            "agronomic_connections": len(self.active_connections),
            "project_connections": sum(len(connections) for connections in self.project_connections.values()),
            "total_gardens_subscribed": len(self.garden_subscriptions),
            "total_projects_active": len(self.project_connections),
            "total_users": len(set(self.active_connections.keys()) | set(self.user_projects.keys())),
            "cursor_positions": sum(len(cursors) for cursors in self.cursor_positions.values())
        }
    
    def cleanup_inactive_connections(self):
        """Clean up inactive connections."""
        current_time = datetime.utcnow()
        inactive_threshold = 300  # 5 minutes
        
        # Clean up agronomic connections
        inactive_users = []
        for user_id, last_activity in self.last_activity.items():
            if (current_time - last_activity).total_seconds() > inactive_threshold:
                inactive_users.append(user_id)
        
        for user_id in inactive_users:
            self.remove_connection(user_id)
        
        # Clean up project connections
        for project_id, connections in list(self.project_connections.items()):
            inactive_project_users = []
            for user_id, websocket in connections.items():
                if user_id in self.last_activity:
                    if (current_time - self.last_activity[user_id]).total_seconds() > inactive_threshold:
                        inactive_project_users.append(user_id)
            
            for user_id in inactive_project_users:
                self.remove_project_connection(project_id, user_id)
        
        logger.info(f"Cleaned up {len(inactive_users)} inactive connections")
    
    # --- Activity Tracking ---
    
    def track_activity(self, user_id: str, activity_type: str, metadata: Optional[Dict[str, Any]] = None):
        """Track user activity."""
        self.last_activity[user_id] = datetime.utcnow()
        
        activity_log = {
            "user_id": user_id,
            "activity_type": activity_type,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        logger.info(f"User activity: {activity_log}")
    
    # --- Error Handling ---
    
    async def handle_connection_error(self, user_id: str, error: Exception):
        """Handle connection errors."""
        logger.error(f"Connection error for user {user_id}: {str(error)}")
        
        # Remove from all connections
        self.remove_connection(user_id)
        
        # Remove from all project connections
        for project_id in list(self.user_projects.get(user_id, set())):
            self.remove_project_connection(project_id, user_id)
        
        # Send error notification if possible
        try:
            error_message = {
                "type": "connection_error",
                "error": str(error),
                "timestamp": datetime.utcnow().isoformat()
            }
            await self.broadcast_to_user(user_id, error_message)
        except Exception as e:
            logger.error(f"Failed to send error notification: {str(e)}")

# Create global instance
websocket_manager = WebSocketManager()
