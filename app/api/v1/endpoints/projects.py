import uuid
import json
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any

from app.services.websocket_manager import manager
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.user import UserPublic
from app.schemas.project import Project, ProjectCreate, ProjectUpdate
from app.utils import UUIDEncoder

router = APIRouter()

# --- In-Memory "Database" for Projects ---
fake_projects_db: Dict[uuid.UUID, Dict[str, Any]] = {}


# --- Project CRUD Endpoints ---

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(
    *,
    project_in: ProjectCreate,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Create a new project for the current user.
    """
    project_id = uuid.uuid4()
    project_data = project_in.model_dump()
    project_data.update({"id": project_id, "owner_id": current_user.id, "layout": {}})
    fake_projects_db[project_id] = project_data
    return Project(**project_data)


@router.get("/", response_model=List[Project])
def read_projects(
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Retrieve all projects owned by the current user.
    """
    user_projects = [
        Project(**p) for p in fake_projects_db.values() if p["owner_id"] == current_user.id
    ]
    return user_projects


@router.get("/{project_id}", response_model=Project)
def read_project(
    *,
    project_id: uuid.UUID,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Get a specific project by ID.
    """
    project = fake_projects_db.get(project_id)
    if not project or project["owner_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return Project(**project)


@router.put("/{project_id}", response_model=Project)
async def update_project(
    *,
    project_id: uuid.UUID,
    project_in: ProjectUpdate,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Update a project. Only the owner can perform this action.
    This will also broadcast the changes to all connected WebSocket clients.
    """
    project = fake_projects_db.get(project_id)
    if not project or project["owner_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    update_data = project_in.model_dump(exclude_unset=True)
    project.update(update_data)
    fake_projects_db[project_id] = project

    # Broadcast the update to all clients in the project room
    await manager.broadcast_to_project(
        str(project_id), json.dumps({"type": "project_updated", "data": project}, cls=UUIDEncoder)
    )

    return Project(**project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    *,
    project_id: uuid.UUID,
    current_user: UserPublic = Depends(get_current_user),
):
    """
    Delete a project. Only the owner can perform this action.
    """
    project = fake_projects_db.get(project_id)
    if not project or project["owner_id"] != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    del fake_projects_db[project_id]

    # Broadcast the deletion to all clients in the project room
    await manager.broadcast_to_project(
        str(project_id), json.dumps({"type": "project_deleted", "project_id": str(project_id)}, cls=UUIDEncoder)
    )

    return


# --- WebSocket Endpoint ---

@router.websocket("/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: str):
    """
    WebSocket endpoint for real-time project collaboration.
    """
    await manager.connect(websocket, project_id)
    try:
        while True:
            # The server can listen for messages from the client if needed.
            # For now, it just keeps the connection open.
            data = await websocket.receive_text()
            # For demonstration, we can echo the message back to the project group.
            await manager.broadcast_to_project(project_id, f"Message from client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)
        await manager.broadcast_to_project(project_id, "A user has disconnected.")
