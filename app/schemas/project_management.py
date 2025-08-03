from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProjectStatus(str, Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    TESTING = "testing"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    TESTING = "testing"
    DONE = "done"
    BLOCKED = "blocked"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BugSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# Base schemas
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    due_date: Optional[datetime] = None
    progress: float = Field(0.0, ge=0.0, le=100.0)
    metadata: Optional[Dict[str, Any]] = None


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, ge=0.0)
    actual_hours: Optional[float] = Field(None, ge=0.0)
    tags: Optional[List[str]] = None


class BugBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    severity: BugSeverity = BugSeverity.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    steps_to_reproduce: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    environment: Optional[str] = None


class FeedbackBase(BaseModel):
    category: str = Field(..., min_length=1, max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    tags: Optional[List[str]] = None


class ReleaseBase(BaseModel):
    version: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    release_notes: Optional[str] = None
    status: str = Field("draft", min_length=1, max_length=50)
    changes: Optional[List[Dict[str, Any]]] = None


class CodeReviewBase(BaseModel):
    pull_request_url: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: str = Field("pending", min_length=1, max_length=50)
    review_data: Optional[Dict[str, Any]] = None


# Create schemas
class ProjectCreate(ProjectBase):
    pass


class TaskCreate(TaskBase):
    project_id: int
    assigned_to: Optional[int] = None


class BugCreate(BugBase):
    project_id: int
    assigned_to: Optional[int] = None


class FeedbackCreate(FeedbackBase):
    project_id: int


class ReleaseCreate(ReleaseBase):
    project_id: int


class CodeReviewCreate(CodeReviewBase):
    project_id: int
    reviewer_id: int
    author_id: int


# Update schemas
class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    due_date: Optional[datetime] = None
    progress: Optional[float] = Field(None, ge=0.0, le=100.0)
    metadata: Optional[Dict[str, Any]] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to: Optional[int] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[float] = Field(None, ge=0.0)
    actual_hours: Optional[float] = Field(None, ge=0.0)
    tags: Optional[List[str]] = None


class BugUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    severity: Optional[BugSeverity] = None
    status: Optional[TaskStatus] = None
    assigned_to: Optional[int] = None
    steps_to_reproduce: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    environment: Optional[str] = None


class FeedbackUpdate(BaseModel):
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[str] = None
    tags: Optional[List[str]] = None


class ReleaseUpdate(BaseModel):
    version: Optional[str] = Field(None, min_length=1, max_length=50)
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    release_notes: Optional[str] = None
    status: Optional[str] = Field(None, min_length=1, max_length=50)
    changes: Optional[List[Dict[str, Any]]] = None


class CodeReviewUpdate(BaseModel):
    pull_request_url: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, min_length=1, max_length=50)
    review_data: Optional[Dict[str, Any]] = None


# Response schemas
class UserSummary(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None

    class Config:
        from_attributes = True


class ProjectCollaboratorResponse(BaseModel):
    id: int
    user: UserSummary
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner: UserSummary
    collaborators: List[ProjectCollaboratorResponse] = []

    class Config:
        from_attributes = True


class TaskResponse(TaskBase):
    id: int
    project_id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    assigned_user: Optional[UserSummary] = None
    creator: UserSummary

    class Config:
        from_attributes = True


class BugResponse(BugBase):
    id: int
    project_id: int
    reported_by: int
    assigned_to: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    reporter: UserSummary
    assigned_user: Optional[UserSummary] = None

    class Config:
        from_attributes = True


class FeedbackResponse(FeedbackBase):
    id: int
    user_id: int
    project_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    user: UserSummary

    class Config:
        from_attributes = True


class ReleaseResponse(ReleaseBase):
    id: int
    project_id: int
    created_by: int
    created_at: datetime
    deployed_at: Optional[datetime] = None
    creator: UserSummary

    class Config:
        from_attributes = True


class CodeReviewResponse(CodeReviewBase):
    id: int
    project_id: int
    reviewer_id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    reviewer: UserSummary
    author: UserSummary

    class Config:
        from_attributes = True


# Metrics schemas
class ProjectMetricsResponse(BaseModel):
    id: int
    project_id: int
    date: datetime
    
    # Development metrics
    lines_of_code: int
    test_coverage: float
    code_quality_score: float
    build_success_rate: float
    
    # Performance metrics
    api_response_time_avg: float
    api_response_time_p95: float
    frontend_load_time: float
    memory_usage: float
    cpu_usage: float
    
    # User metrics
    active_users: int
    new_users: int
    feature_adoption_rate: float
    
    # Bug metrics
    bugs_total: int
    bugs_open: int
    bugs_resolved: int
    bugs_critical: int
    
    # Task metrics
    tasks_total: int
    tasks_completed: int
    tasks_in_progress: int
    tasks_overdue: int

    class Config:
        from_attributes = True


class UserActivityResponse(BaseModel):
    id: int
    user_id: int
    project_id: int
    activity_type: str
    activity_data: Optional[Dict[str, Any]] = None
    timestamp: datetime
    session_id: Optional[str] = None
    user: UserSummary

    class Config:
        from_attributes = True


# Dashboard schemas
class DashboardMetrics(BaseModel):
    total_projects: int
    active_projects: int
    total_tasks: int
    completed_tasks: int
    total_bugs: int
    open_bugs: int
    critical_bugs: int
    total_users: int
    active_users: int
    average_response_time: float
    test_coverage_avg: float
    code_quality_avg: float


class ProjectProgress(BaseModel):
    project_id: int
    project_name: str
    progress: float
    status: ProjectStatus
    due_date: Optional[datetime] = None
    tasks_completed: int
    tasks_total: int
    bugs_open: int
    bugs_resolved: int


class KanbanBoard(BaseModel):
    project_id: int
    columns: Dict[str, List[TaskResponse]]  # status -> tasks


class ProjectAnalytics(BaseModel):
    project_id: int
    project_name: str
    metrics: ProjectMetricsResponse
    recent_activities: List[UserActivityResponse]
    top_contributors: List[UserSummary]
    recent_feedback: List[FeedbackResponse]


# List response schemas
class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]
    total: int
    page: int
    size: int


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    page: int
    size: int


class BugListResponse(BaseModel):
    bugs: List[BugResponse]
    total: int
    page: int
    size: int


class FeedbackListResponse(BaseModel):
    feedback: List[FeedbackResponse]
    total: int
    page: int
    size: int


class ReleaseListResponse(BaseModel):
    releases: List[ReleaseResponse]
    total: int
    page: int
    size: int


class CodeReviewListResponse(BaseModel):
    reviews: List[CodeReviewResponse]
    total: int
    page: int
    size: int 