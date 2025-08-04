from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from api.deps import get_current_user, get_db
from crud.project_management import (
    project_crud, task_crud, bug_crud, feedback_crud, 
    release_crud, code_review_crud, project_metrics_crud, user_activity_crud
)
from schemas.project_management import (
    ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse,
    TaskCreate, TaskUpdate, TaskResponse, TaskListResponse,
    BugCreate, BugUpdate, BugResponse, BugListResponse,
    FeedbackCreate, FeedbackUpdate, FeedbackResponse, FeedbackListResponse,
    ReleaseCreate, ReleaseUpdate, ReleaseResponse, ReleaseListResponse,
    CodeReviewCreate, CodeReviewUpdate, CodeReviewResponse, CodeReviewListResponse,
    DashboardMetrics, ProjectProgress, KanbanBoard, ProjectAnalytics,
    ProjectMetricsResponse, UserActivityResponse
)
from models.user import User

router = APIRouter()


# Dashboard endpoints
@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard metrics for the current user"""
    metrics = project_crud.get_dashboard_metrics(db, current_user.id)
    return DashboardMetrics(**metrics)


@router.get("/dashboard/progress", response_model=List[ProjectProgress])
async def get_project_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get progress data for all user's projects"""
    progress_data = project_crud.get_project_progress(db, current_user.id)
    return [ProjectProgress(**data) for data in progress_data]


# Project endpoints
@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new project"""
    project = project_crud.create(db, project_data, current_user.id)
    
    # Log activity
    user_activity_crud.create(
        db, current_user.id, project.id, "project_created",
        {"project_name": project.name}
    )
    
    return project


@router.get("/projects", response_model=ProjectListResponse)
async def get_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all projects for the current user"""
    projects = project_crud.get_by_user(db, current_user.id, skip, limit)
    total = len(projects)  # In a real app, you'd get total count separately
    
    return ProjectListResponse(
        projects=projects,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific project"""
    project = project_crud.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if user has access to this project
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    return project


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a project"""
    project = project_crud.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this project"
        )
    
    updated_project = project_crud.update(db, project_id, project_data)
    
    # Log activity
    user_activity_crud.create(
        db, current_user.id, project_id, "project_updated",
        {"project_name": updated_project.name}
    )
    
    return updated_project


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project"""
    project = project_crud.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this project"
        )
    
    success = project_crud.delete(db, project_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete project"
        )
    
    return {"message": "Project deleted successfully"}


# Task endpoints
@router.post("/projects/{project_id}/tasks", response_model=TaskResponse)
async def create_task(
    project_id: int,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task"""
    # Verify project exists and user has access
    project = project_crud.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks in this project"
        )
    
    task = task_crud.create(db, task_data, current_user.id)
    
    # Log activity
    user_activity_crud.create(
        db, current_user.id, project_id, "task_created",
        {"task_title": task.title}
    )
    
    return task


@router.get("/projects/{project_id}/tasks", response_model=TaskListResponse)
async def get_tasks(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tasks for a project"""
    # Verify project exists and user has access
    project = project_crud.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    tasks = task_crud.get_by_project(db, project_id, skip, limit)
    total = len(tasks)  # In a real app, you'd get total count separately
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/projects/{project_id}/kanban", response_model=KanbanBoard)
async def get_kanban_board(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get kanban board for a project"""
    # Verify project exists and user has access
    project = project_crud.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    columns = task_crud.get_kanban_board(db, project_id)
    return KanbanBoard(project_id=project_id, columns=columns)


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific task"""
    task = task_crud.get(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access to the project
    project = project_crud.get(db, task.project_id)
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )
    
    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task"""
    task = task_crud.get(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access to the project
    project = project_crud.get(db, task.project_id)
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )
    
    updated_task = task_crud.update(db, task_id, task_data)
    
    # Log activity
    user_activity_crud.create(
        db, current_user.id, task.project_id, "task_updated",
        {"task_title": updated_task.title, "new_status": updated_task.status.value}
    )
    
    return updated_task


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task"""
    task = task_crud.get(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if user has access to the project
    project = project_crud.get(db, task.project_id)
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )
    
    success = task_crud.delete(db, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete task"
        )
    
    return {"message": "Task deleted successfully"}


# Bug endpoints
@router.post("/projects/{project_id}/bugs", response_model=BugResponse)
async def create_bug(
    project_id: int,
    bug_data: BugCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new bug report"""
    # Verify project exists and user has access
    project = project_crud.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create bugs in this project"
        )
    
    bug = bug_crud.create(db, bug_data, current_user.id)
    
    # Log activity
    user_activity_crud.create(
        db, current_user.id, project_id, "bug_created",
        {"bug_title": bug.title, "severity": bug.severity.value}
    )
    
    return bug


@router.get("/projects/{project_id}/bugs", response_model=BugListResponse)
async def get_bugs(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all bugs for a project"""
    # Verify project exists and user has access
    project = project_crud.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    bugs = bug_crud.get_by_project(db, project_id, skip, limit)
    total = len(bugs)  # In a real app, you'd get total count separately
    
    return BugListResponse(
        bugs=bugs,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/bugs/{bug_id}", response_model=BugResponse)
async def get_bug(
    bug_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific bug"""
    bug = bug_crud.get(db, bug_id)
    if not bug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bug not found"
        )
    
    # Check if user has access to the project
    project = project_crud.get(db, bug.project_id)
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this bug"
        )
    
    return bug


@router.put("/bugs/{bug_id}", response_model=BugResponse)
async def update_bug(
    bug_id: int,
    bug_data: BugUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a bug"""
    bug = bug_crud.get(db, bug_id)
    if not bug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bug not found"
        )
    
    # Check if user has access to the project
    project = project_crud.get(db, bug.project_id)
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this bug"
        )
    
    updated_bug = bug_crud.update(db, bug_id, bug_data)
    
    # Log activity
    user_activity_crud.create(
        db, current_user.id, bug.project_id, "bug_updated",
        {"bug_title": updated_bug.title, "new_status": updated_bug.status.value}
    )
    
    return updated_bug


@router.delete("/bugs/{bug_id}")
async def delete_bug(
    bug_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a bug"""
    bug = bug_crud.get(db, bug_id)
    if not bug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bug not found"
        )
    
    # Check if user has access to the project
    project = project_crud.get(db, bug.project_id)
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this bug"
        )
    
    success = bug_crud.delete(db, bug_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete bug"
        )
    
    return {"message": "Bug deleted successfully"}


# Feedback endpoints
@router.post("/projects/{project_id}/feedback", response_model=FeedbackResponse)
async def create_feedback(
    project_id: int,
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new feedback"""
    # Verify project exists and user has access
    project = project_crud.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create feedback for this project"
        )
    
    feedback = feedback_crud.create(db, feedback_data, current_user.id)
    
    # Log activity
    user_activity_crud.create(
        db, current_user.id, project_id, "feedback_created",
        {"feedback_title": feedback.title, "category": feedback.category}
    )
    
    return feedback


@router.get("/projects/{project_id}/feedback", response_model=FeedbackListResponse)
async def get_feedback(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all feedback for a project"""
    # Verify project exists and user has access
    project = project_crud.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    feedback_list = feedback_crud.get_by_project(db, project_id, skip, limit)
    total = len(feedback_list)  # In a real app, you'd get total count separately
    
    return FeedbackListResponse(
        feedback=feedback_list,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


# Analytics endpoints
@router.get("/projects/{project_id}/analytics", response_model=ProjectAnalytics)
async def get_project_analytics(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics for a project"""
    # Verify project exists and user has access
    project = project_crud.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project"
        )
    
    # Get latest metrics
    metrics = project_metrics_crud.get_latest(db, project_id)
    if not metrics:
        # Create default metrics if none exist
        metrics = project_metrics_crud.create(db, project_id, {
            "lines_of_code": 0,
            "test_coverage": 0.0,
            "code_quality_score": 0.0,
            "build_success_rate": 0.0,
            "api_response_time_avg": 0.0,
            "api_response_time_p95": 0.0,
            "frontend_load_time": 0.0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
            "active_users": 0,
            "new_users": 0,
            "feature_adoption_rate": 0.0,
            "bugs_total": 0,
            "bugs_open": 0,
            "bugs_resolved": 0,
            "bugs_critical": 0,
            "tasks_total": 0,
            "tasks_completed": 0,
            "tasks_in_progress": 0,
            "tasks_overdue": 0
        })
    
    # Get recent activities
    recent_activities = user_activity_crud.get_recent_activities(db, project_id, 20)
    
    # Get recent feedback
    recent_feedback = feedback_crud.get_by_project(db, project_id, 0, 10)
    
    # Get top contributors (simplified - in real app you'd calculate based on activity)
    top_contributors = []
    if project.collaborators:
        top_contributors = [c.user for c in project.collaborators[:5]]
    
    return ProjectAnalytics(
        project_id=project_id,
        project_name=project.name,
        metrics=metrics,
        recent_activities=recent_activities,
        top_contributors=top_contributors,
        recent_feedback=recent_feedback
    )


# Activity tracking endpoint
@router.post("/projects/{project_id}/activity")
async def track_activity(
    project_id: int,
    activity_type: str,
    activity_data: dict = None,
    session_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Track user activity"""
    # Verify project exists and user has access
    project = project_crud.get(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project.owner_id != current_user.id and not any(
        c.user_id == current_user.id for c in project.collaborators
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to track activity for this project"
        )
    
    activity = user_activity_crud.create(
        db, current_user.id, project_id, activity_type, activity_data, session_id
    )
    
    return {"message": "Activity tracked successfully", "activity_id": activity.id} 