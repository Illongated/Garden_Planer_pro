from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..models.audit import AuditLog, ChangeType
import uuid

async def create_audit_log_entry(
    db: AsyncSession,
    *,
    user_id: uuid.UUID | None,
    project_id: uuid.UUID | None,
    target_entity: str,
    target_id: str,
    change_type: ChangeType,
    change_diff: dict,
) -> AuditLog:
    """Creates a new entry in the audit log."""
    db_log = AuditLog(
        user_id=user_id,
        project_id=project_id,
        target_entity=target_entity,
        target_id=target_id,
        change_type=change_type,
        change_diff=change_diff,
    )
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

async def get_audit_logs_for_project(
    db: AsyncSession, project_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[AuditLog]:
    """Get all audit logs for a specific project."""
    result = await db.execute(
        select(AuditLog)
        .filter(AuditLog.project_id == project_id)
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_audit_logs_for_user(
    db: AsyncSession, user_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[AuditLog]:
    """Get all audit logs initiated by a specific user."""
    result = await db.execute(
        select(AuditLog)
        .filter(AuditLog.user_id == user_id)
        .order_by(AuditLog.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
