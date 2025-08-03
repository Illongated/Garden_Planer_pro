import uuid
import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query, Path
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.user import UserPublic
from app.schemas.project import (
    Project, ProjectCreate, ProjectUpdate, ProjectDetail, ProjectList,
    ProjectMember, ProjectMemberCreate, ProjectMemberUpdate,
    ProjectVersion, ProjectVersionCreate,
    ProjectComment, ProjectCommentCreate, ProjectCommentUpdate,
    ProjectActivity, ProjectFilter, ProjectSort, ProjectExport, ProjectImport,
    ProjectWebSocketMessage, ProjectCollaborationMessage,
    ProjectPermission, ProjectStatus
)
from app.crud.project import project_crud, project_member_crud, project_version_crud, project_comment_crud
from app.services.websocket_manager import websocket_manager
from app.services.project_export_service import project_export_service
from app.utils import UUIDEncoder

router = APIRouter()

# --- Project CRUD Endpoints ---

@router.post("/", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(
    *,
    db: Session = Depends(get_db),
    project_in: ProjectCreate,
    current_user: UserPublic = Depends(get_current_user),
):
    """Create a new project."""
    try:
        project = project_crud.create_project(
            db=db, project_in=project_in, owner_id=current_user.id
        )
        
        # Broadcast to WebSocket clients
        await websocket_manager.broadcast_to_user(
            current_user.id,
            ProjectWebSocketMessage(
                type="project_created",
                project_id=project.id,
                data=Project.model_validate(project).model_dump(),
                user_id=current_user.id,
                user_name=current_user.full_name
            ).model_dump()
        )
        
        return project
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create project: {str(e)}"
        )

@router.get("/", response_model=ProjectList)
def read_projects(
    *,
    db: Session = Depends(get_db),
    current_user: UserPublic = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[ProjectStatus] = Query(None),
    search: Optional[str] = Query(None, max_length=100),
):
    """Get projects for the current user with pagination and filtering."""
    projects, total = project_crud.get_user_projects(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
        search=search
    )
    
    return ProjectList(
        projects=projects,
        total=total,
        page=skip // limit + 1,
        size=limit,
        has_next=skip + limit < total,
        has_prev=skip > 0
    )

@router.get("/public", response_model=ProjectList)
def read_public_projects(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, max_length=100),
    climate_zone: Optional[str] = Query(None),
    soil_type: Optional[str] = Query(None),
):
    """Get public projects with filtering."""
    projects, total = project_crud.get_public_projects(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        climate_zone=climate_zone,
        soil_type=soil_type
    )
    
    return ProjectList(
        projects=projects,
        total=total,
        page=skip // limit + 1,
        size=limit,
        has_next=skip + limit < total,
        has_prev=skip > 0
    )

@router.get("/{project_id}", response_model=ProjectDetail)
def read_project(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    current_user: UserPublic = Depends(get_current_user),
):
    """Get a specific project with all details."""
    project = project_crud.get_project_with_details(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check permissions
    if not project_crud.check_user_permission(
        db=db, project_id=project_id, user_id=current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this project"
        )
    
    return project

@router.put("/{project_id}", response_model=Project)
async def update_project(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    project_in: ProjectUpdate,
    current_user: UserPublic = Depends(get_current_user),
):
    """Update a project."""
    # Check permissions
    if not project_crud.check_user_permission(
        db=db, project_id=project_id, user_id=current_user.id, required_permission=ProjectPermission.EDITOR
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to edit this project"
        )
    
    project = project_crud.update_project(
        db=db, project_id=project_id, project_in=project_in, user_id=current_user.id
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Broadcast to WebSocket clients
    await websocket_manager.broadcast_to_project(
        str(project_id),
        ProjectWebSocketMessage(
            type="project_updated",
            project_id=project_id,
            data=Project.model_validate(project).model_dump(),
            user_id=current_user.id,
            user_name=current_user.full_name
        ).model_dump()
    )
    
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    current_user: UserPublic = Depends(get_current_user),
):
    """Delete a project (soft delete)."""
    success = project_crud.delete_project(
        db=db, project_id=project_id, user_id=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you don't have permission to delete it"
        )
    
    # Broadcast to WebSocket clients
    await websocket_manager.broadcast_to_project(
        str(project_id),
        ProjectWebSocketMessage(
            type="project_deleted",
            project_id=project_id,
            data={"project_id": str(project_id)},
            user_id=current_user.id,
            user_name=current_user.full_name
        ).model_dump()
    )

# --- Project Member Endpoints ---

@router.post("/{project_id}/members", response_model=ProjectMember)
def add_project_member(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    member_in: ProjectMemberCreate,
    current_user: UserPublic = Depends(get_current_user),
):
    """Add a member to a project."""
    # Check permissions
    if not project_crud.check_user_permission(
        db=db, project_id=project_id, user_id=current_user.id, required_permission=ProjectPermission.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to add members"
        )
    
    member = project_member_crud.add_member(
        db=db, project_id=project_id, member_in=member_in, invited_by=current_user.id
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found or already a member"
        )
    
    return member

@router.get("/{project_id}/members", response_model=List[ProjectMember])
def get_project_members(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    current_user: UserPublic = Depends(get_current_user),
):
    """Get all members of a project."""
    # Check permissions
    if not project_crud.check_user_permission(
        db=db, project_id=project_id, user_id=current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view members"
        )
    
    return project_member_crud.get_project_members(db=db, project_id=project_id)

@router.put("/{project_id}/members/{user_id}", response_model=ProjectMember)
def update_member_permission(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    user_id: uuid.UUID = Path(...),
    member_update: ProjectMemberUpdate,
    current_user: UserPublic = Depends(get_current_user),
):
    """Update member permission."""
    # Check permissions
    if not project_crud.check_user_permission(
        db=db, project_id=project_id, user_id=current_user.id, required_permission=ProjectPermission.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update member permissions"
        )
    
    member = project_member_crud.update_member_permission(
        db=db, project_id=project_id, user_id=user_id, 
        permission=member_update.permission, updated_by=current_user.id
    )
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    return member

@router.delete("/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_project_member(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    user_id: uuid.UUID = Path(...),
    current_user: UserPublic = Depends(get_current_user),
):
    """Remove a member from a project."""
    # Check permissions
    if not project_crud.check_user_permission(
        db=db, project_id=project_id, user_id=current_user.id, required_permission=ProjectPermission.ADMIN
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to remove members"
        )
    
    success = project_member_crud.remove_member(
        db=db, project_id=project_id, user_id=user_id, removed_by=current_user.id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

# --- Project Version Endpoints ---

@router.post("/{project_id}/versions", response_model=ProjectVersion)
def create_project_version(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    version_in: ProjectVersionCreate,
    current_user: UserPublic = Depends(get_current_user),
):
    """Create a new project version."""
    # Check permissions
    if not project_crud.check_user_permission(
        db=db, project_id=project_id, user_id=current_user.id, required_permission=ProjectPermission.EDITOR
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create versions"
        )
    
    try:
        version = project_version_crud.create_version(
            db=db, project_id=project_id, version_in=version_in, created_by=current_user.id
        )
        return version
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/{project_id}/versions", response_model=List[ProjectVersion])
def get_project_versions(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserPublic = Depends(get_current_user),
):
    """Get versions of a project."""
    # Check permissions
    if not project_crud.check_user_permission(
        db=db, project_id=project_id, user_id=current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view versions"
        )
    
    versions, _ = project_version_crud.get_project_versions(
        db=db, project_id=project_id, skip=skip, limit=limit
    )
    return versions

@router.post("/{project_id}/versions/{version_id}/revert", response_model=Project)
def revert_to_version(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    version_id: uuid.UUID = Path(...),
    current_user: UserPublic = Depends(get_current_user),
):
    """Revert project to a specific version."""
    # Check permissions
    if not project_crud.check_user_permission(
        db=db, project_id=project_id, user_id=current_user.id, required_permission=ProjectPermission.EDITOR
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to revert versions"
        )
    
    project = project_version_crud.revert_to_version(
        db=db, project_id=project_id, version_id=version_id, user_id=current_user.id
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project or version not found"
        )
    
    return project

# --- Project Comment Endpoints ---

@router.post("/{project_id}/comments", response_model=ProjectComment)
def create_project_comment(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    comment_in: ProjectCommentCreate,
    current_user: UserPublic = Depends(get_current_user),
):
    """Create a new project comment."""
    # Check permissions
    if not project_crud.check_user_permission(
        db=db, project_id=project_id, user_id=current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to add comments"
        )
    
    comment = project_comment_crud.create_comment(
        db=db, project_id=project_id, comment_in=comment_in, author_id=current_user.id
    )
    return comment

@router.get("/{project_id}/comments", response_model=List[ProjectComment])
def get_project_comments(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserPublic = Depends(get_current_user),
):
    """Get comments for a project."""
    # Check permissions
    if not project_crud.check_user_permission(
        db=db, project_id=project_id, user_id=current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view comments"
        )
    
    comments, _ = project_comment_crud.get_project_comments(
        db=db, project_id=project_id, skip=skip, limit=limit
    )
    return comments

@router.post("/{project_id}/comments/{comment_id}/resolve", response_model=ProjectComment)
def resolve_comment(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    comment_id: uuid.UUID = Path(...),
    current_user: UserPublic = Depends(get_current_user),
):
    """Mark a comment as resolved."""
    # Check permissions
    if not project_crud.check_user_permission(
        db=db, project_id=project_id, user_id=current_user.id, required_permission=ProjectPermission.EDITOR
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to resolve comments"
        )
    
    comment = project_comment_crud.resolve_comment(
        db=db, comment_id=comment_id, resolved_by=current_user.id
    )
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    return comment

# --- Project Export/Import Endpoints ---

@router.get("/{project_id}/export", response_model=ProjectExport)
def export_project(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    current_user: UserPublic = Depends(get_current_user),
):
    """Export a project with all its data."""
    # Check permissions
    if not project_crud.check_user_permission(
        db=db, project_id=project_id, user_id=current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to export this project"
        )
    
    return project_export_service.export_project(db=db, project_id=project_id)

@router.get("/{project_id}/export/json")
def export_project_json(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    current_user: UserPublic = Depends(get_current_user),
):
    """Export a project as JSON file."""
    # Check permissions
    if not project_crud.check_user_permission(
        db=db, project_id=project_id, user_id=current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to export this project"
        )
    
    file_path = project_export_service.export_to_json(db=db, project_id=project_id)
    return FileResponse(
        path=file_path,
        media_type="application/json",
        filename=f"project_{project_id}.json"
    )

@router.get("/{project_id}/export/pdf")
def export_project_pdf(
    *,
    db: Session = Depends(get_db),
    project_id: uuid.UUID = Path(...),
    current_user: UserPublic = Depends(get_current_user),
):
    """Export a project as PDF file."""
    # Check permissions
    if not project_crud.check_user_permission(
        db=db, project_id=project_id, user_id=current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to export this project"
        )
    
    file_path = project_export_service.export_to_pdf(db=db, project_id=project_id)
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"project_{project_id}.pdf"
    )

@router.post("/import", response_model=Project)
def import_project(
    *,
    db: Session = Depends(get_db),
    project_import: ProjectImport,
    current_user: UserPublic = Depends(get_current_user),
):
    """Import a project from JSON data."""
    try:
        project = project_export_service.import_project(
            db=db, project_import=project_import, owner_id=current_user.id
        )
        return project
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to import project: {str(e)}"
        )

# --- WebSocket Endpoint for Real-time Collaboration ---

@router.websocket("/ws/{project_id}")
async def project_websocket(
    websocket: WebSocket,
    project_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time project collaboration."""
    await websocket.accept()
    
    try:
        # Validate user token and get user
        # This is a simplified version - in production, you'd validate the JWT token
        user_id = websocket_manager.validate_token(token)
        if not user_id:
            await websocket.close(code=4001, reason="Invalid token")
            return
        
        # Check project permissions
        if not project_crud.check_user_permission(
            db=db, project_id=uuid.UUID(project_id), user_id=user_id
        ):
            await websocket.close(code=4003, reason="Insufficient permissions")
            return
        
        # Add connection to project room
        websocket_manager.add_project_connection(project_id, user_id, websocket)
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "project_id": project_id,
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Broadcast user joined
        await websocket_manager.broadcast_to_project(
            project_id,
            ProjectCollaborationMessage(
                type="user_joined",
                project_id=uuid.UUID(project_id),
                user_id=user_id,
                user_name="User",  # You'd get this from the user object
                data={"user_id": str(user_id)}
            ).model_dump()
        )
        
        # Handle incoming messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }))
            elif message.get("type") == "cursor_update":
                # Broadcast cursor position to other users
                await websocket_manager.broadcast_to_project(
                    project_id,
                    ProjectCollaborationMessage(
                        type="cursor_update",
                        project_id=uuid.UUID(project_id),
                        user_id=user_id,
                        user_name="User",
                        data=message.get("data", {})
                    ).model_dump(),
                    exclude_user_id=user_id
                )
            elif message.get("type") == "layout_update":
                # Handle real-time layout updates
                await websocket_manager.broadcast_to_project(
                    project_id,
                    ProjectCollaborationMessage(
                        type="layout_update",
                        project_id=uuid.UUID(project_id),
                        user_id=user_id,
                        user_name="User",
                        data=message.get("data", {})
                    ).model_dump(),
                    exclude_user_id=user_id
                )
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close(code=4000, reason=f"Error: {str(e)}")
    finally:
        # Remove connection and broadcast user left
        websocket_manager.remove_project_connection(project_id, user_id)
        await websocket_manager.broadcast_to_project(
            project_id,
            ProjectCollaborationMessage(
                type="user_left",
                project_id=uuid.UUID(project_id),
                user_id=user_id,
                user_name="User",
                data={"user_id": str(user_id)}
            ).model_dump()
        )
