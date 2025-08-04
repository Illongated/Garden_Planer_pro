import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.exc import IntegrityError

from app.models.project import Project, ProjectMember, ProjectVersion, ProjectComment, ProjectActivity, ProjectPermission, ProjectStatus
from app.models.user import User
from schemas.project import ProjectCreate, ProjectUpdate, ProjectMemberCreate, ProjectVersionCreate, ProjectCommentCreate

class ProjectCRUD:
    """CRUD operations for projects."""
    
    def create_project(self, db: Session, *, project_in: ProjectCreate, owner_id: uuid.UUID) -> Project:
        """Create a new project."""
        project_data = project_in.model_dump()
        project_data["owner_id"] = owner_id
        project_data["current_version"] = 1
        
        db_project = Project(**project_data)
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        
        # Create initial version
        initial_version = ProjectVersion(
            project_id=db_project.id,
            version_number=1,
            created_by=owner_id,
            name="Initial Version",
            description="Initial project version",
            layout_data=project_data.get("layout_data"),
            plant_data=project_data.get("plant_data"),
            irrigation_data=project_data.get("irrigation_data")
        )
        db.add(initial_version)
        
        # Create activity log
        activity = ProjectActivity(
            project_id=db_project.id,
            user_id=owner_id,
            activity_type="project_created",
            description=f"Project '{db_project.name}' was created"
        )
        db.add(activity)
        
        db.commit()
        return db_project
    
    def get_project(self, db: Session, project_id: uuid.UUID) -> Optional[Project]:
        """Get a project by ID."""
        return db.query(Project).filter(Project.id == project_id).first()
    
    def get_project_with_details(self, db: Session, project_id: uuid.UUID) -> Optional[Project]:
        """Get a project with all related data."""
        return db.query(Project).options(
            joinedload(Project.owner),
            joinedload(Project.last_modified_user),
            joinedload(Project.members).joinedload(ProjectMember.user),
            joinedload(Project.versions),
            joinedload(Project.comments).joinedload(ProjectComment.author),
            joinedload(Project.activities).joinedload(ProjectActivity.user)
        ).filter(Project.id == project_id).first()
    
    def get_user_projects(
        self, 
        db: Session, 
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ProjectStatus] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Project], int]:
        """Get projects for a user with pagination and filtering."""
        query = db.query(Project).filter(
            or_(
                Project.owner_id == user_id,
                Project.members.any(ProjectMember.user_id == user_id)
            )
        )
        
        if status:
            query = query.filter(Project.status == status)
        
        if search:
            search_filter = or_(
                Project.name.ilike(f"%{search}%"),
                Project.description.ilike(f"%{search}%"),
                Project.location.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        total = query.count()
        projects = query.offset(skip).limit(limit).all()
        
        return projects, total
    
    def get_public_projects(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        climate_zone: Optional[str] = None,
        soil_type: Optional[str] = None
    ) -> Tuple[List[Project], int]:
        """Get public projects with filtering."""
        query = db.query(Project).filter(Project.is_public == True, Project.status == ProjectStatus.ACTIVE)
        
        if search:
            search_filter = or_(
                Project.name.ilike(f"%{search}%"),
                Project.description.ilike(f"%{search}%"),
                Project.location.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if climate_zone:
            query = query.filter(Project.climate_zone == climate_zone)
        
        if soil_type:
            query = query.filter(Project.soil_type == soil_type)
        
        total = query.count()
        projects = query.offset(skip).limit(limit).all()
        
        return projects, total
    
    def update_project(
        self, 
        db: Session, 
        *, 
        project_id: uuid.UUID, 
        project_in: ProjectUpdate, 
        user_id: uuid.UUID
    ) -> Optional[Project]:
        """Update a project."""
        db_project = self.get_project(db, project_id)
        if not db_project:
            return None
        
        update_data = project_in.model_dump(exclude_unset=True)
        
        # Create new version if layout/plant/irrigation data changed
        if any(key in update_data for key in ["layout_data", "plant_data", "irrigation_data"]):
            new_version = ProjectVersion(
                project_id=project_id,
                version_number=db_project.current_version + 1,
                created_by=user_id,
                name=f"Version {db_project.current_version + 1}",
                description="Auto-generated version",
                layout_data=update_data.get("layout_data", db_project.layout_data),
                plant_data=update_data.get("plant_data", db_project.plant_data),
                irrigation_data=update_data.get("irrigation_data", db_project.irrigation_data)
            )
            db.add(new_version)
            update_data["current_version"] = db_project.current_version + 1
        
        update_data["last_modified_by"] = user_id
        
        for field, value in update_data.items():
            setattr(db_project, field, value)
        
        # Create activity log
        activity = ProjectActivity(
            project_id=project_id,
            user_id=user_id,
            activity_type="project_updated",
            description=f"Project '{db_project.name}' was updated",
            metadata={"updated_fields": list(update_data.keys())}
        )
        db.add(activity)
        
        db.commit()
        db.refresh(db_project)
        return db_project
    
    def delete_project(self, db: Session, *, project_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete a project (soft delete)."""
        db_project = self.get_project(db, project_id)
        if not db_project or db_project.owner_id != user_id:
            return False
        
        db_project.status = ProjectStatus.DELETED
        
        # Create activity log
        activity = ProjectActivity(
            project_id=project_id,
            user_id=user_id,
            activity_type="project_deleted",
            description=f"Project '{db_project.name}' was deleted"
        )
        db.add(activity)
        
        db.commit()
        return True
    
    def check_user_permission(
        self, 
        db: Session, 
        *, 
        project_id: uuid.UUID, 
        user_id: uuid.UUID, 
        required_permission: ProjectPermission = ProjectPermission.VIEWER
    ) -> bool:
        """Check if user has required permission for project."""
        project = self.get_project(db, project_id)
        if not project:
            return False
        
        # Owner has all permissions
        if project.owner_id == user_id:
            return True
        
        # Check member permissions
        member = db.query(ProjectMember).filter(
            and_(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id
            )
        ).first()
        
        if not member:
            return False
        
        permission_hierarchy = {
            ProjectPermission.OWNER: 4,
            ProjectPermission.ADMIN: 3,
            ProjectPermission.EDITOR: 2,
            ProjectPermission.VIEWER: 1
        }
        
        return permission_hierarchy.get(member.permission, 0) >= permission_hierarchy.get(required_permission, 0)

class ProjectMemberCRUD:
    """CRUD operations for project members."""
    
    def add_member(
        self, 
        db: Session, 
        *, 
        project_id: uuid.UUID, 
        member_in: ProjectMemberCreate, 
        invited_by: uuid.UUID
    ) -> Optional[ProjectMember]:
        """Add a member to a project."""
        # Find user by email
        user = db.query(User).filter(User.email == member_in.user_email).first()
        if not user:
            return None
        
        # Check if already a member
        existing_member = db.query(ProjectMember).filter(
            and_(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user.id
            )
        ).first()
        
        if existing_member:
            return existing_member
        
        member_data = member_in.model_dump()
        member_data.update({
            "project_id": project_id,
            "user_id": user.id,
            "invited_by": invited_by,
            "invited_at": datetime.utcnow()
        })
        
        db_member = ProjectMember(**member_data)
        db.add(db_member)
        
        # Create activity log
        activity = ProjectActivity(
            project_id=project_id,
            user_id=invited_by,
            activity_type="member_added",
            description=f"User {user.email} was added to the project",
            metadata={"member_email": user.email, "permission": member_data["permission"]}
        )
        db.add(activity)
        
        db.commit()
        db.refresh(db_member)
        return db_member
    
    def update_member_permission(
        self, 
        db: Session, 
        *, 
        project_id: uuid.UUID, 
        user_id: uuid.UUID, 
        permission: ProjectPermission,
        updated_by: uuid.UUID
    ) -> Optional[ProjectMember]:
        """Update member permission."""
        member = db.query(ProjectMember).filter(
            and_(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id
            )
        ).first()
        
        if not member:
            return None
        
        old_permission = member.permission
        member.permission = permission
        
        # Create activity log
        activity = ProjectActivity(
            project_id=project_id,
            user_id=updated_by,
            activity_type="member_permission_updated",
            description=f"Member permission updated from {old_permission} to {permission}",
            metadata={"member_user_id": user_id, "old_permission": old_permission, "new_permission": permission}
        )
        db.add(activity)
        
        db.commit()
        db.refresh(member)
        return member
    
    def remove_member(
        self, 
        db: Session, 
        *, 
        project_id: uuid.UUID, 
        user_id: uuid.UUID,
        removed_by: uuid.UUID
    ) -> bool:
        """Remove a member from a project."""
        member = db.query(ProjectMember).filter(
            and_(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id
            )
        ).first()
        
        if not member:
            return False
        
        # Create activity log
        activity = ProjectActivity(
            project_id=project_id,
            user_id=removed_by,
            activity_type="member_removed",
            description=f"Member was removed from the project",
            metadata={"removed_user_id": user_id}
        )
        db.add(activity)
        
        db.delete(member)
        db.commit()
        return True
    
    def get_project_members(
        self, 
        db: Session, 
        project_id: uuid.UUID
    ) -> List[ProjectMember]:
        """Get all members of a project."""
        return db.query(ProjectMember).options(
            joinedload(ProjectMember.user),
            joinedload(ProjectMember.inviter)
        ).filter(ProjectMember.project_id == project_id).all()

class ProjectVersionCRUD:
    """CRUD operations for project versions."""
    
    def create_version(
        self, 
        db: Session, 
        *, 
        project_id: uuid.UUID, 
        version_in: ProjectVersionCreate, 
        created_by: uuid.UUID
    ) -> ProjectVersion:
        """Create a new project version."""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError("Project not found")
        
        version_data = version_in.model_dump()
        version_data.update({
            "project_id": project_id,
            "created_by": created_by,
            "version_number": project.current_version + 1
        })
        
        db_version = ProjectVersion(**version_data)
        db.add(db_version)
        
        # Update project current version
        project.current_version = version_data["version_number"]
        
        # Create activity log
        activity = ProjectActivity(
            project_id=project_id,
            user_id=created_by,
            activity_type="version_created",
            description=f"Version '{version_in.name}' was created",
            metadata={"version_number": version_data["version_number"]}
        )
        db.add(activity)
        
        db.commit()
        db.refresh(db_version)
        return db_version
    
    def get_project_versions(
        self, 
        db: Session, 
        project_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[ProjectVersion], int]:
        """Get versions of a project."""
        query = db.query(ProjectVersion).filter(ProjectVersion.project_id == project_id)
        total = query.count()
        versions = query.order_by(desc(ProjectVersion.version_number)).offset(skip).limit(limit).all()
        return versions, total
    
    def get_version(
        self, 
        db: Session, 
        version_id: uuid.UUID
    ) -> Optional[ProjectVersion]:
        """Get a specific version."""
        return db.query(ProjectVersion).filter(ProjectVersion.id == version_id).first()
    
    def revert_to_version(
        self, 
        db: Session, 
        *, 
        project_id: uuid.UUID, 
        version_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> Optional[Project]:
        """Revert project to a specific version."""
        version = self.get_version(db, version_id)
        if not version or version.project_id != project_id:
            return None
        
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return None
        
        # Create new version with reverted data
        new_version = ProjectVersion(
            project_id=project_id,
            version_number=project.current_version + 1,
            created_by=user_id,
            name=f"Revert to version {version.version_number}",
            description=f"Reverted to version '{version.name}'",
            layout_data=version.layout_data,
            plant_data=version.plant_data,
            irrigation_data=version.irrigation_data
        )
        db.add(new_version)
        
        # Update project data
        project.layout_data = version.layout_data
        project.plant_data = version.plant_data
        project.irrigation_data = version.irrigation_data
        project.current_version = new_version.version_number
        project.last_modified_by = user_id
        
        # Create activity log
        activity = ProjectActivity(
            project_id=project_id,
            user_id=user_id,
            activity_type="version_reverted",
            description=f"Project reverted to version {version.version_number}",
            metadata={"reverted_version_id": str(version_id)}
        )
        db.add(activity)
        
        db.commit()
        db.refresh(project)
        return project

class ProjectCommentCRUD:
    """CRUD operations for project comments."""
    
    def create_comment(
        self, 
        db: Session, 
        *, 
        project_id: uuid.UUID, 
        comment_in: ProjectCommentCreate, 
        author_id: uuid.UUID
    ) -> ProjectComment:
        """Create a new project comment."""
        comment_data = comment_in.model_dump()
        comment_data.update({
            "project_id": project_id,
            "author_id": author_id
        })
        
        db_comment = ProjectComment(**comment_data)
        db.add(db_comment)
        
        # Create activity log
        activity = ProjectActivity(
            project_id=project_id,
            user_id=author_id,
            activity_type="comment_added",
            description="A comment was added to the project",
            metadata={"comment_id": str(db_comment.id)}
        )
        db.add(activity)
        
        db.commit()
        db.refresh(db_comment)
        return db_comment
    
    def get_project_comments(
        self, 
        db: Session, 
        project_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[ProjectComment], int]:
        """Get comments for a project."""
        query = db.query(ProjectComment).filter(ProjectComment.project_id == project_id)
        total = query.count()
        comments = query.order_by(desc(ProjectComment.created_at)).offset(skip).limit(limit).all()
        return comments, total
    
    def resolve_comment(
        self, 
        db: Session, 
        *, 
        comment_id: uuid.UUID, 
        resolved_by: uuid.UUID
    ) -> Optional[ProjectComment]:
        """Mark a comment as resolved."""
        comment = db.query(ProjectComment).filter(ProjectComment.id == comment_id).first()
        if not comment:
            return None
        
        comment.is_resolved = True
        comment.resolved_by = resolved_by
        comment.resolved_at = datetime.utcnow()
        
        # Create activity log
        activity = ProjectActivity(
            project_id=comment.project_id,
            user_id=resolved_by,
            activity_type="comment_resolved",
            description="A comment was resolved",
            metadata={"comment_id": str(comment_id)}
        )
        db.add(activity)
        
        db.commit()
        db.refresh(comment)
        return comment

# Create instances
project_crud = ProjectCRUD()
project_member_crud = ProjectMemberCRUD()
project_version_crud = ProjectVersionCRUD()
project_comment_crud = ProjectCommentCRUD() 