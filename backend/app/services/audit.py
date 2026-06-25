from uuid import UUID

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    aid_request_id: UUID,
    actor_user_id: UUID,
    action: str,
    old_status: str | None,
    new_status: str | None,
    notes: str | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        aid_request_id=aid_request_id,
        actor_user_id=actor_user_id,
        action=action,
        old_status=old_status,
        new_status=new_status,
        notes=notes,
    )

    db.add(audit_log)

    return audit_log