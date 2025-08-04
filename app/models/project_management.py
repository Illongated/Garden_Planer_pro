from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import uuid4
import uuid

from sqlalchemy import String, DateTime, Text, Boolean, ForeignKey, JSON, Float, Enum, Integer, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base
import enum


class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    TESTING = "testing"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"


class TaskStatus(str, enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    TESTING = "testing"
    DONE = "done"
    BLOCKED = "blocked"


class TaskPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class BugSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class PMProject(Base):
    __tablename__ = "pm_projects"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.PLANNING, index=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0)  # 0-100
    project_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Additional project data
    
    # Relationships
    owner = relationship("User", back_populates="pm_projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    bugs = relationship("Bug", back_populates="project", cascade="all, delete-orphan")
    metrics = relationship("ProjectMetrics", back_populates="project", cascade="all, delete-orphan")
    collaborators = relationship("ProjectCollaborator", back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.TODO, index=True)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), default=TaskPriority.MEDIUM, index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pm_projects.id"), nullable=False)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    due_date = Column(DateTime(timezone=True))
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    tags = Column(JSON)  # Array of tags
    
    # Relationships
    project = relationship("PMProject", back_populates="tasks")
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    creator = relationship("User", foreign_keys=[created_by])


class Bug(Base):
    __tablename__ = "bugs"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[BugSeverity] = mapped_column(Enum(BugSeverity), default=BugSeverity.MEDIUM, index=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.TODO, index=True)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pm_projects.id"), nullable=False)
    reported_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True))
    steps_to_reproduce = Column(Text)
    expected_behavior = Column(Text)
    actual_behavior = Column(Text)
    environment = Column(String(255))  # Browser, OS, etc.
    
    # Relationships
    project = relationship("PMProject", back_populates="bugs")
    reporter = relationship("User", foreign_keys=[reported_by])
    assigned_user = relationship("User", foreign_keys=[assigned_to])


class ProjectCollaborator(Base):
    __tablename__ = "project_collaborators"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pm_projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(50), default="member")  # owner, admin, member, viewer
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("PMProject", back_populates="collaborators")
    user = relationship("User")


class ProjectMetrics(Base):
    __tablename__ = "project_metrics"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pm_projects.id"), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Development metrics
    lines_of_code = Column(Integer, default=0)
    test_coverage = Column(Float, default=0.0)
    code_quality_score = Column(Float, default=0.0)
    build_success_rate = Column(Float, default=0.0)
    
    # Performance metrics
    api_response_time_avg = Column(Float, default=0.0)
    api_response_time_p95 = Column(Float, default=0.0)
    frontend_load_time = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    cpu_usage = Column(Float, default=0.0)
    
    # User metrics
    active_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
    feature_adoption_rate = Column(Float, default=0.0)
    
    # Bug metrics
    bugs_total = Column(Integer, default=0)
    bugs_open = Column(Integer, default=0)
    bugs_resolved = Column(Integer, default=0)
    bugs_critical = Column(Integer, default=0)
    
    # Task metrics
    tasks_total = Column(Integer, default=0)
    tasks_completed = Column(Integer, default=0)
    tasks_in_progress = Column(Integer, default=0)
    tasks_overdue = Column(Integer, default=0)
    
    # Relationships
    project = relationship("PMProject", back_populates="metrics")


class UserActivity(Base):
    __tablename__ = "user_activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("pm_projects.id"), nullable=False)
    activity_type = Column(String(100), nullable=False)  # login, feature_use, bug_report, etc.
    activity_data = Column(JSON)  # Additional activity data
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    session_id = Column(String(255))
    
    # Relationships
    user = relationship("User")
    project = relationship("PMProject")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("pm_projects.id"), nullable=False)
    category = Column(String(100), nullable=False)  # bug, feature, general, performance
    title = Column(String(255), nullable=False)
    description = Column(Text)
    rating = Column(Integer)  # 1-5 rating
    status = Column(String(50), default="open")  # open, in_progress, resolved, closed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True))
    tags = Column(JSON)
    
    # Relationships
    user = relationship("User")
    project = relationship("PMProject")


class Release(Base):
    __tablename__ = "releases"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pm_projects.id"), nullable=False)
    version = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    release_notes = Column(Text)
    status = Column(String(50), default="draft")  # draft, ready, deployed, archived
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deployed_at = Column(DateTime(timezone=True))
    changes = Column(JSON)  # List of changes/features/bug fixes
    
    # Relationships
    project = relationship("PMProject")
    creator = relationship("User")


class CodeReview(Base):
    __tablename__ = "code_reviews"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("pm_projects.id"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pull_request_url = Column(String(500))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="pending")  # pending, approved, changes_requested, merged
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    review_data = Column(JSON)  # Review comments, suggestions, etc.
    
    # Relationships
    project = relationship("PMProject")
    reviewer = relationship("User", foreign_keys=[reviewer_id])
    author = relationship("User", foreign_keys=[author_id]) 