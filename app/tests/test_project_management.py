import pytest
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.project import Project, ProjectMember, ProjectVersion, ProjectComment, ProjectActivity, ProjectPermission, ProjectStatus
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectMemberCreate, ProjectVersionCreate, ProjectCommentCreate
from app.crud.project import project_crud, project_member_crud, project_version_crud, project_comment_crud
from app.services.project_export_service import project_export_service


class TestProjectCRUD:
    """Test project CRUD operations."""
    
    def test_create_project(self, db: Session, test_user: User):
        """Test creating a new project."""
        project_data = ProjectCreate(
            name="Test Garden Project",
            description="A test garden project",
            location="Backyard",
            climate_zone="5b",
            soil_type="Loamy soil",
            garden_size=25.5,
            is_public=False,
            allow_comments=True,
            allow_forking=True
        )
        
        project = project_crud.create_project(
            db=db, project_in=project_data, owner_id=test_user.id
        )
        
        assert project.name == "Test Garden Project"
        assert project.description == "A test garden project"
        assert project.owner_id == test_user.id
        assert project.status == ProjectStatus.DRAFT
        assert project.current_version == 1
        assert project.is_public == False
        
        # Check that initial version was created
        versions = db.query(ProjectVersion).filter(ProjectVersion.project_id == project.id).all()
        assert len(versions) == 1
        assert versions[0].version_number == 1
        assert versions[0].name == "Initial Version"
        
        # Check that activity was logged
        activities = db.query(ProjectActivity).filter(ProjectActivity.project_id == project.id).all()
        assert len(activities) == 1
        assert activities[0].activity_type == "project_created"
    
    def test_get_project(self, db: Session, test_user: User):
        """Test getting a project by ID."""
        # Create a project first
        project_data = ProjectCreate(name="Test Project", description="Test description")
        project = project_crud.create_project(db=db, project_in=project_data, owner_id=test_user.id)
        
        # Get the project
        retrieved_project = project_crud.get_project(db=db, project_id=project.id)
        
        assert retrieved_project is not None
        assert retrieved_project.id == project.id
        assert retrieved_project.name == "Test Project"
    
    def test_get_user_projects(self, db: Session, test_user: User):
        """Test getting projects for a user."""
        # Create multiple projects
        project1 = project_crud.create_project(
            db=db, 
            project_in=ProjectCreate(name="Project 1"), 
            owner_id=test_user.id
        )
        project2 = project_crud.create_project(
            db=db, 
            project_in=ProjectCreate(name="Project 2"), 
            owner_id=test_user.id
        )
        
        projects, total = project_crud.get_user_projects(db=db, user_id=test_user.id)
        
        assert total == 2
        assert len(projects) == 2
        assert any(p.id == project1.id for p in projects)
        assert any(p.id == project2.id for p in projects)
    
    def test_update_project(self, db: Session, test_user: User):
        """Test updating a project."""
        # Create a project
        project = project_crud.create_project(
            db=db, 
            project_in=ProjectCreate(name="Original Name"), 
            owner_id=test_user.id
        )
        
        # Update the project
        update_data = ProjectUpdate(
            name="Updated Name",
            description="Updated description",
            status=ProjectStatus.ACTIVE
        )
        
        updated_project = project_crud.update_project(
            db=db, project_id=project.id, project_in=update_data, user_id=test_user.id
        )
        
        assert updated_project.name == "Updated Name"
        assert updated_project.description == "Updated description"
        assert updated_project.status == ProjectStatus.ACTIVE
        assert updated_project.current_version == 2  # New version created
    
    def test_delete_project(self, db: Session, test_user: User):
        """Test deleting a project (soft delete)."""
        # Create a project
        project = project_crud.create_project(
            db=db, 
            project_in=ProjectCreate(name="To Delete"), 
            owner_id=test_user.id
        )
        
        # Delete the project
        success = project_crud.delete_project(
            db=db, project_id=project.id, user_id=test_user.id
        )
        
        assert success == True
        
        # Check that project is soft deleted
        deleted_project = project_crud.get_project(db=db, project_id=project.id)
        assert deleted_project.status == ProjectStatus.DELETED


class TestProjectMemberCRUD:
    """Test project member CRUD operations."""
    
    def test_add_member(self, db: Session, test_user: User, test_project: Project):
        """Test adding a member to a project."""
        # Create another user
        other_user = User(
            email="member@example.com",
            full_name="Test Member",
            hashed_password="hashed_password"
        )
        db.add(other_user)
        db.commit()
        
        member_data = ProjectMemberCreate(
            user_email="member@example.com",
            permission=ProjectPermission.EDITOR
        )
        
        member = project_member_crud.add_member(
            db=db, project_id=test_project.id, member_in=member_data, invited_by=test_user.id
        )
        
        assert member is not None
        assert member.user_email == "member@example.com"
        assert member.permission == ProjectPermission.EDITOR
        assert member.invited_by == test_user.id
    
    def test_update_member_permission(self, db: Session, test_user: User, test_project: Project):
        """Test updating member permission."""
        # Add a member first
        other_user = User(email="member@example.com", hashed_password="hashed_password")
        db.add(other_user)
        db.commit()
        
        member_data = ProjectMemberCreate(user_email="member@example.com", permission=ProjectPermission.VIEWER)
        member = project_member_crud.add_member(
            db=db, project_id=test_project.id, member_in=member_data, invited_by=test_user.id
        )
        
        # Update permission
        updated_member = project_member_crud.update_member_permission(
            db=db, project_id=test_project.id, user_id=other_user.id, 
            permission=ProjectPermission.ADMIN, updated_by=test_user.id
        )
        
        assert updated_member.permission == ProjectPermission.ADMIN
    
    def test_remove_member(self, db: Session, test_user: User, test_project: Project):
        """Test removing a member from a project."""
        # Add a member first
        other_user = User(email="member@example.com", hashed_password="hashed_password")
        db.add(other_user)
        db.commit()
        
        member_data = ProjectMemberCreate(user_email="member@example.com", permission=ProjectPermission.VIEWER)
        member = project_member_crud.add_member(
            db=db, project_id=test_project.id, member_in=member_data, invited_by=test_user.id
        )
        
        # Remove member
        success = project_member_crud.remove_member(
            db=db, project_id=test_project.id, user_id=other_user.id, removed_by=test_user.id
        )
        
        assert success == True
        
        # Check that member is removed
        members = project_member_crud.get_project_members(db=db, project_id=test_project.id)
        assert len(members) == 0


class TestProjectVersionCRUD:
    """Test project version CRUD operations."""
    
    def test_create_version(self, db: Session, test_user: User, test_project: Project):
        """Test creating a new project version."""
        version_data = ProjectVersionCreate(
            name="Test Version",
            description="A test version",
            layout_data={"test": "data"},
            is_tagged=True,
            tag_name="v1.0"
        )
        
        version = project_version_crud.create_version(
            db=db, project_id=test_project.id, version_in=version_data, created_by=test_user.id
        )
        
        assert version.name == "Test Version"
        assert version.description == "A test version"
        assert version.version_number == test_project.current_version + 1
        assert version.is_tagged == True
        assert version.tag_name == "v1.0"
        
        # Check that project version was updated
        updated_project = project_crud.get_project(db=db, project_id=test_project.id)
        assert updated_project.current_version == version.version_number
    
    def test_get_project_versions(self, db: Session, test_user: User, test_project: Project):
        """Test getting versions of a project."""
        # Create multiple versions
        version1 = project_version_crud.create_version(
            db=db, project_id=test_project.id, 
            version_in=ProjectVersionCreate(name="Version 1"), 
            created_by=test_user.id
        )
        version2 = project_version_crud.create_version(
            db=db, project_id=test_project.id, 
            version_in=ProjectVersionCreate(name="Version 2"), 
            created_by=test_user.id
        )
        
        versions, total = project_version_crud.get_project_versions(db=db, project_id=test_project.id)
        
        assert total >= 3  # Including initial version
        assert len(versions) >= 3
        assert versions[0].version_number > versions[1].version_number  # Ordered by version number desc
    
    def test_revert_to_version(self, db: Session, test_user: User, test_project: Project):
        """Test reverting to a specific version."""
        # Create a version with specific data
        version_data = ProjectVersionCreate(
            name="Revert Target",
            layout_data={"revert": "data"},
            plant_data={"plants": "data"}
        )
        version = project_version_crud.create_version(
            db=db, project_id=test_project.id, version_in=version_data, created_by=test_user.id
        )
        
        # Revert to this version
        reverted_project = project_version_crud.revert_to_version(
            db=db, project_id=test_project.id, version_id=version.id, user_id=test_user.id
        )
        
        assert reverted_project.layout_data == {"revert": "data"}
        assert reverted_project.plant_data == {"plants": "data"}
        assert reverted_project.current_version == version.version_number + 1


class TestProjectCommentCRUD:
    """Test project comment CRUD operations."""
    
    def test_create_comment(self, db: Session, test_user: User, test_project: Project):
        """Test creating a new project comment."""
        comment_data = ProjectCommentCreate(
            content="This is a test comment",
            position_x=100.0,
            position_y=200.0,
            element_id="test_element"
        )
        
        comment = project_comment_crud.create_comment(
            db=db, project_id=test_project.id, comment_in=comment_data, author_id=test_user.id
        )
        
        assert comment.content == "This is a test comment"
        assert comment.position_x == 100.0
        assert comment.position_y == 200.0
        assert comment.element_id == "test_element"
        assert comment.author_id == test_user.id
    
    def test_get_project_comments(self, db: Session, test_user: User, test_project: Project):
        """Test getting comments for a project."""
        # Create multiple comments
        comment1 = project_comment_crud.create_comment(
            db=db, project_id=test_project.id,
            comment_in=ProjectCommentCreate(content="Comment 1"),
            author_id=test_user.id
        )
        comment2 = project_comment_crud.create_comment(
            db=db, project_id=test_project.id,
            comment_in=ProjectCommentCreate(content="Comment 2"),
            author_id=test_user.id
        )
        
        comments, total = project_comment_crud.get_project_comments(db=db, project_id=test_project.id)
        
        assert total == 2
        assert len(comments) == 2
        assert any(c.content == "Comment 1" for c in comments)
        assert any(c.content == "Comment 2" for c in comments)
    
    def test_resolve_comment(self, db: Session, test_user: User, test_project: Project):
        """Test resolving a comment."""
        # Create a comment
        comment = project_comment_crud.create_comment(
            db=db, project_id=test_project.id,
            comment_in=ProjectCommentCreate(content="Test comment"),
            author_id=test_user.id
        )
        
        # Resolve the comment
        resolved_comment = project_comment_crud.resolve_comment(
            db=db, comment_id=comment.id, resolved_by=test_user.id
        )
        
        assert resolved_comment.is_resolved == True
        assert resolved_comment.resolved_by == test_user.id
        assert resolved_comment.resolved_at is not None


class TestProjectPermissions:
    """Test project permission checking."""
    
    def test_owner_permissions(self, db: Session, test_user: User, test_project: Project):
        """Test that project owner has all permissions."""
        assert project_crud.check_user_permission(
            db=db, project_id=test_project.id, user_id=test_user.id, 
            required_permission=ProjectPermission.OWNER
        ) == True
        
        assert project_crud.check_user_permission(
            db=db, project_id=test_project.id, user_id=test_user.id, 
            required_permission=ProjectPermission.ADMIN
        ) == True
        
        assert project_crud.check_user_permission(
            db=db, project_id=test_project.id, user_id=test_user.id, 
            required_permission=ProjectPermission.EDITOR
        ) == True
        
        assert project_crud.check_user_permission(
            db=db, project_id=test_project.id, user_id=test_user.id, 
            required_permission=ProjectPermission.VIEWER
        ) == True
    
    def test_member_permissions(self, db: Session, test_user: User, test_project: Project):
        """Test member permissions."""
        # Create another user and add as member
        other_user = User(email="member@example.com", hashed_password="hashed_password")
        db.add(other_user)
        db.commit()
        
        member_data = ProjectMemberCreate(user_email="member@example.com", permission=ProjectPermission.EDITOR)
        project_member_crud.add_member(
            db=db, project_id=test_project.id, member_in=member_data, invited_by=test_user.id
        )
        
        # Test permissions
        assert project_crud.check_user_permission(
            db=db, project_id=test_project.id, user_id=other_user.id, 
            required_permission=ProjectPermission.VIEWER
        ) == True
        
        assert project_crud.check_user_permission(
            db=db, project_id=test_project.id, user_id=other_user.id, 
            required_permission=ProjectPermission.EDITOR
        ) == True
        
        assert project_crud.check_user_permission(
            db=db, project_id=test_project.id, user_id=other_user.id, 
            required_permission=ProjectPermission.ADMIN
        ) == False  # Editor cannot access admin functions


class TestProjectExportService:
    """Test project export service."""
    
    def test_export_project(self, db: Session, test_user: User, test_project: Project):
        """Test exporting a project."""
        export_data = project_export_service.export_project(db=db, project_id=test_project.id)
        
        assert export_data.project.id == test_project.id
        assert export_data.project.name == test_project.name
        assert len(export_data.versions) >= 1  # At least initial version
        assert len(export_data.activities) >= 1  # At least creation activity
    
    def test_export_to_json(self, db: Session, test_user: User, test_project: Project):
        """Test exporting project to JSON."""
        file_path = project_export_service.export_to_json(db=db, project_id=test_project.id)
        
        assert file_path is not None
        assert file_path.endswith('.json')
        
        # Check that file exists and contains valid JSON
        import json
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        assert 'project' in data
        assert data['project']['id'] == str(test_project.id)
        assert data['project']['name'] == test_project.name
    
    def test_import_project(self, db: Session, test_user: User):
        """Test importing a project."""
        from app.schemas.project import ProjectImport
        
        import_data = ProjectImport(
            name="Imported Project",
            description="An imported project",
            layout_data={"imported": "data"},
            plant_data={"plants": "imported"},
            import_metadata={"source": "test"}
        )
        
        imported_project = project_export_service.import_project(
            db=db, project_import=import_data, owner_id=test_user.id
        )
        
        assert imported_project.name == "Imported Project"
        assert imported_project.description == "An imported project"
        assert imported_project.owner_id == test_user.id
        assert imported_project.layout_data == {"imported": "data"}
        assert imported_project.plant_data == {"plants": "imported"}


# Fixtures
@pytest.fixture
def test_project(db: Session, test_user: User) -> Project:
    """Create a test project."""
    project_data = ProjectCreate(
        name="Test Project",
        description="A test project for testing",
        location="Test Location",
        climate_zone="5b",
        soil_type="Test soil",
        garden_size=10.0
    )
    return project_crud.create_project(db=db, project_in=project_data, owner_id=test_user.id) 