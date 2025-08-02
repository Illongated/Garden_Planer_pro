from sqlalchemy import Column, String, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import BaseModel, UUID
import enum

class ChangeType(str, enum.Enum):
    create = "CREATE"
    update = "UPDATE"
    delete = "DELETE"

class AuditLog(BaseModel):
    """
    Logs changes made to key entities in the database for auditing purposes.
    """
    __tablename__ = "audit_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True) # User who made the change (null for system changes)
    project_id = Column(UUID(as_uuid=True), ForeignKey("garden_projects.id"), nullable=True, index=True) # Associated project

    target_entity = Column(String(100), nullable=False, index=True) # e.g., 'PlantInstance'
    target_id = Column(String, nullable=False, index=True) # The ID of the entity that was changed

    change_type = Column(Enum(ChangeType), nullable=False)

    # Use JSONB for efficient querying of changes
    change_diff = Column(JSONB, nullable=False) # e.g., {'old': {'status': 'growing'}, 'new': {'status': 'harvested'}}

    user = relationship("User", back_populates="audit_logs")
    project = relationship("GardenProject", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, target='{self.target_entity}:{self.target_id}')>"
