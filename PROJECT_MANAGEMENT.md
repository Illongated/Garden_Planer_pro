# Project Management System

## Overview

The Agrotique Garden Planner's Project Management System provides a comprehensive solution for managing garden projects with advanced collaboration features, version control, and real-time communication. This system enables users to create, share, and collaborate on garden projects with granular permissions and full audit trails.

## Features

### Core Project Management
- **Full CRUD Operations**: Create, read, update, and delete garden projects
- **Project Metadata**: Name, description, location, climate zone, soil type, garden size
- **Status Management**: Draft, Active, Archived, Deleted states
- **Public/Private Projects**: Control project visibility and access

### Advanced Collaboration
- **Granular Permissions**: Owner, Admin, Editor, Viewer roles
- **Member Management**: Invite, manage, and remove project members
- **Real-time Collaboration**: WebSocket-based live updates and cursor tracking
- **Inline Comments**: Position-specific comments with resolution tracking

### Version Control System
- **Git-like Versioning**: Complete version history with branching
- **Automatic Versioning**: Auto-create versions on significant changes
- **Manual Versioning**: Create tagged versions with custom names
- **Revert Functionality**: Rollback to any previous version
- **Version Comparison**: Diff and merge capabilities

### Export/Import System
- **Multi-format Export**: JSON, PDF, PNG formats
- **Complete Data Export**: Projects with all versions, comments, and activities
- **Import Functionality**: Import projects from external sources
- **Backup/Restore**: Full project backup and restoration

### Real-time Features
- **WebSocket Communication**: Bidirectional real-time updates
- **Live Collaboration**: Multiple users editing simultaneously
- **Cursor Tracking**: See other users' cursor positions
- **Activity Feed**: Real-time project activity updates

## Architecture

### Database Models

#### Project
```python
class Project(Base):
    id: UUID
    name: str
    description: str
    status: ProjectStatus
    owner_id: UUID
    location: str
    climate_zone: str
    soil_type: str
    garden_size: float
    layout_data: JSONB
    plant_data: JSONB
    irrigation_data: JSONB
    current_version: int
    last_modified_by: UUID
    is_public: bool
    allow_comments: bool
    allow_forking: bool
```

#### ProjectMember
```python
class ProjectMember(Base):
    project_id: UUID
    user_id: UUID
    permission: ProjectPermission
    invited_by: UUID
    invited_at: datetime
    accepted_at: datetime
```

#### ProjectVersion
```python
class ProjectVersion(Base):
    project_id: UUID
    version_number: int
    created_by: UUID
    name: str
    description: str
    layout_data: JSONB
    plant_data: JSONB
    irrigation_data: JSONB
    is_tagged: bool
    tag_name: str
    parent_version_id: UUID
```

#### ProjectComment
```python
class ProjectComment(Base):
    project_id: UUID
    author_id: UUID
    parent_comment_id: UUID
    content: str
    position_x: float
    position_y: float
    element_id: str
    is_resolved: bool
    resolved_by: UUID
    resolved_at: datetime
```

#### ProjectActivity
```python
class ProjectActivity(Base):
    project_id: UUID
    user_id: UUID
    activity_type: str
    description: str
    metadata: JSONB
```

### Permission System

The system implements a hierarchical permission model:

1. **Owner**: Full control over the project
   - Can delete the project
   - Can manage all members
   - Can change project settings
   - Has all permissions

2. **Admin**: High-level project management
   - Can add/remove members
   - Can change member permissions
   - Can manage project settings
   - Cannot delete the project

3. **Editor**: Content management
   - Can edit project content
   - Can create versions
   - Can add comments
   - Cannot manage members

4. **Viewer**: Read-only access
   - Can view project content
   - Can add comments (if enabled)
   - Cannot make changes

### API Endpoints

#### Project Management
```
POST   /api/v1/projects/                    # Create project
GET    /api/v1/projects/                    # List user projects
GET    /api/v1/projects/public              # List public projects
GET    /api/v1/projects/{project_id}        # Get project details
PUT    /api/v1/projects/{project_id}        # Update project
DELETE /api/v1/projects/{project_id}        # Delete project
```

#### Member Management
```
POST   /api/v1/projects/{project_id}/members           # Add member
GET    /api/v1/projects/{project_id}/members           # List members
PUT    /api/v1/projects/{project_id}/members/{user_id} # Update member
DELETE /api/v1/projects/{project_id}/members/{user_id} # Remove member
```

#### Version Control
```
POST   /api/v1/projects/{project_id}/versions                    # Create version
GET    /api/v1/projects/{project_id}/versions                    # List versions
POST   /api/v1/projects/{project_id}/versions/{version_id}/revert # Revert to version
```

#### Comments
```
POST   /api/v1/projects/{project_id}/comments                    # Add comment
GET    /api/v1/projects/{project_id}/comments                    # List comments
POST   /api/v1/projects/{project_id}/comments/{comment_id}/resolve # Resolve comment
```

#### Export/Import
```
GET    /api/v1/projects/{project_id}/export                      # Export project data
GET    /api/v1/projects/{project_id}/export/json                 # Export as JSON
GET    /api/v1/projects/{project_id}/export/pdf                  # Export as PDF
POST   /api/v1/projects/import                                   # Import project
```

#### Real-time Collaboration
```
WS     /api/v1/projects/ws/{project_id}                         # WebSocket endpoint
```

## Usage Examples

### Creating a Project
```python
from app.schemas.project import ProjectCreate

project_data = ProjectCreate(
    name="Backyard Vegetable Garden",
    description="A comprehensive vegetable garden layout",
    location="Backyard, Zone 5",
    climate_zone="5b",
    soil_type="Loamy soil",
    garden_size=25.5,
    is_public=True,
    allow_comments=True,
    allow_forking=True
)

project = project_crud.create_project(
    db=db, project_in=project_data, owner_id=user.id
)
```

### Adding a Member
```python
from app.schemas.project import ProjectMemberCreate

member_data = ProjectMemberCreate(
    user_email="collaborator@example.com",
    permission=ProjectPermission.EDITOR
)

member = project_member_crud.add_member(
    db=db, project_id=project.id, member_in=member_data, invited_by=user.id
)
```

### Creating a Version
```python
from app.schemas.project import ProjectVersionCreate

version_data = ProjectVersionCreate(
    name="Spring Layout Update",
    description="Updated layout for spring planting",
    layout_data={"plants": [...]},
    is_tagged=True,
    tag_name="v2.0"
)

version = project_version_crud.create_version(
    db=db, project_id=project.id, version_in=version_data, created_by=user.id
)
```

### Adding a Comment
```python
from app.schemas.project import ProjectCommentCreate

comment_data = ProjectCommentCreate(
    content="This spacing looks perfect for companion planting!",
    position_x=150.0,
    position_y=200.0,
    element_id="tomato_1"
)

comment = project_comment_crud.create_comment(
    db=db, project_id=project.id, comment_in=comment_data, author_id=user.id
)
```

### Real-time Collaboration
```javascript
// Connect to project WebSocket
const ws = new WebSocket(`ws://localhost:8000/api/v1/projects/ws/${projectId}?token=${userToken}`);

// Send cursor position
ws.send(JSON.stringify({
    type: 'cursor_update',
    data: { x: 100, y: 200 }
}));

// Send layout update
ws.send(JSON.stringify({
    type: 'layout_update',
    data: { plants: [...] }
}));

// Listen for updates
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === 'cursor_update') {
        updateOtherUserCursor(message.data);
    }
};
```

## Export/Import System

### Export Formats

#### JSON Export
```python
# Export complete project data
export_data = project_export_service.export_project(db=db, project_id=project.id)

# Export to JSON file
file_path = project_export_service.export_to_json(db=db, project_id=project.id)
```

#### PDF Export
```python
# Export project as PDF report
file_path = project_export_service.export_to_pdf(db=db, project_id=project.id)
```

#### PNG Export
```python
# Export project layout as image
file_path = project_export_service.export_to_png(db=db, project_id=project.id)
```

### Import System
```python
from app.schemas.project import ProjectImport

import_data = ProjectImport(
    name="Imported Garden Project",
    description="Project imported from external source",
    layout_data={"plants": [...]},
    plant_data={"catalog": [...]},
    import_metadata={"source": "external_file.json"}
)

imported_project = project_export_service.import_project(
    db=db, project_import=import_data, owner_id=user.id
)
```

## WebSocket Protocol

### Connection
```
WS /api/v1/projects/ws/{project_id}?token={user_token}
```

### Message Types

#### Client to Server
```javascript
// Cursor update
{
    "type": "cursor_update",
    "data": {
        "x": 100,
        "y": 200
    }
}

// Layout update
{
    "type": "layout_update",
    "data": {
        "plants": [...],
        "zones": [...]
    }
}

// Ping
{
    "type": "ping"
}
```

#### Server to Client
```javascript
// User joined
{
    "type": "user_joined",
    "project_id": "uuid",
    "user_id": "uuid",
    "user_name": "John Doe",
    "data": {"user_id": "uuid"}
}

// Cursor update from other user
{
    "type": "cursor_update",
    "project_id": "uuid",
    "user_id": "uuid",
    "user_name": "Jane Smith",
    "data": {"x": 150, "y": 250}
}

// Layout update
{
    "type": "layout_update",
    "project_id": "uuid",
    "user_id": "uuid",
    "user_name": "John Doe",
    "data": {"plants": [...]}
}

// Pong response
{
    "type": "pong",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control
- Project-level permissions
- Activity logging and audit trails

### Data Protection
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection

### Real-time Security
- WebSocket authentication
- Connection validation
- Rate limiting
- Message validation

## Performance Optimizations

### Database Optimization
- Indexed queries for fast project retrieval
- Efficient pagination
- Optimized joins for related data
- Connection pooling

### Caching Strategy
- Redis caching for frequently accessed data
- Project metadata caching
- User session caching
- Query result caching

### Real-time Performance
- WebSocket connection pooling
- Message batching
- Efficient broadcasting
- Connection health monitoring

## Testing

### Unit Tests
```bash
# Run project management tests
pytest app/tests/test_project_management.py -v
```

### Integration Tests
```bash
# Run full test suite
pytest app/tests/ -v
```

### Test Coverage
```bash
# Generate coverage report
pytest --cov=app app/tests/test_project_management.py
```

## Deployment

### Database Migration
```bash
# Run migrations
alembic upgrade head
```

### Environment Variables
```bash
# Required environment variables
DATABASE_URL=postgresql://user:pass@localhost/garden_planner
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

## Monitoring & Logging

### Application Logs
- Structured logging with correlation IDs
- Error tracking and alerting
- Performance monitoring
- User activity analytics

### Health Checks
- Database connectivity
- Redis connectivity
- WebSocket connection health
- API endpoint availability

## Future Enhancements

### Planned Features
- Advanced search and filtering
- Project templates and cloning
- Advanced version branching
- Real-time conflict resolution
- Advanced export formats (SVG, DXF)
- Mobile app support
- Offline synchronization
- Advanced analytics and reporting

### Scalability Improvements
- Horizontal scaling support
- Microservices architecture
- Advanced caching strategies
- CDN integration
- Load balancing optimization

## Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up database: `alembic upgrade head`
4. Run tests: `pytest app/tests/test_project_management.py`

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints throughout
- Write comprehensive tests
- Document all public APIs
- Follow security best practices

## Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Contact the development team
- Check the documentation
- Review the test suite for examples 