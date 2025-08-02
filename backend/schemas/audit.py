import uuid
from pydantic import BaseModel, Field
from datetime import datetime
from ..models.audit import ChangeType

# --- Base Schema ---

class AuditLogBase(BaseModel):
    user_id: uuid.UUID | None
    project_id: uuid.UUID | None
    target_entity: str
    target_id: str
    change_type: ChangeType
    change_diff: dict

# --- Public Schema (for API responses) ---

class AuditLog(AuditLogBase):
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True
