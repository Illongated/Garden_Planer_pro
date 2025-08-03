from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, validates, relationship
from app.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .garden import Garden
    from .project import Project, ProjectMember, ProjectComment, ProjectActivity
    from .project_management import Project as PMProject, Task, Bug, ProjectCollaborator, UserActivity, Feedback, Release, CodeReview

class User(Base):
    """User model."""
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    gardens: Mapped[list["Garden"]] = relationship("Garden", back_populates="owner", cascade="all, delete-orphan")
    owned_projects: Mapped[list["Project"]] = relationship("Project", foreign_keys="Project.owner_id", back_populates="owner", cascade="all, delete-orphan")
    project_memberships: Mapped[list["ProjectMember"]] = relationship("ProjectMember", foreign_keys="ProjectMember.user_id", back_populates="user", cascade="all, delete-orphan")
    project_comments: Mapped[list["ProjectComment"]] = relationship("ProjectComment", foreign_keys="ProjectComment.author_id", back_populates="author", cascade="all, delete-orphan")
    project_activities: Mapped[list["ProjectActivity"]] = relationship("ProjectActivity", foreign_keys="ProjectActivity.user_id", back_populates="user", cascade="all, delete-orphan")
    
    # Project Management relationships
    pm_projects: Mapped[list["PMProject"]] = relationship("Project", foreign_keys="PMProject.owner_id", back_populates="owner", cascade="all, delete-orphan")
    created_tasks: Mapped[list["Task"]] = relationship("Task", foreign_keys="Task.created_by", back_populates="creator", cascade="all, delete-orphan")
    assigned_tasks: Mapped[list["Task"]] = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assigned_user")
    reported_bugs: Mapped[list["Bug"]] = relationship("Bug", foreign_keys="Bug.reported_by", back_populates="reporter", cascade="all, delete-orphan")
    assigned_bugs: Mapped[list["Bug"]] = relationship("Bug", foreign_keys="Bug.assigned_to", back_populates="assigned_user")
    project_collaborations: Mapped[list["ProjectCollaborator"]] = relationship("ProjectCollaborator", foreign_keys="ProjectCollaborator.user_id", back_populates="user", cascade="all, delete-orphan")
    user_activities: Mapped[list["UserActivity"]] = relationship("UserActivity", foreign_keys="UserActivity.user_id", back_populates="user", cascade="all, delete-orphan")
    feedback_submissions: Mapped[list["Feedback"]] = relationship("Feedback", foreign_keys="Feedback.user_id", back_populates="user", cascade="all, delete-orphan")
    created_releases: Mapped[list["Release"]] = relationship("Release", foreign_keys="Release.created_by", back_populates="creator", cascade="all, delete-orphan")
    code_reviews_as_reviewer: Mapped[list["CodeReview"]] = relationship("CodeReview", foreign_keys="CodeReview.reviewer_id", back_populates="reviewer", cascade="all, delete-orphan")
    code_reviews_as_author: Mapped[list["CodeReview"]] = relationship("CodeReview", foreign_keys="CodeReview.author_id", back_populates="author", cascade="all, delete-orphan")

    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError("Email cannot be empty.")
        if '@' not in email:
            raise ValueError("Invalid email address format.")
        return email.lower()

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
