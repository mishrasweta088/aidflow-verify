from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_roles
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.schemas.audit_log import AuditLogResponse

router = APIRouter(prefix="/audit-logs", tags=["audit logs"])


@router.get("/aid-request/{aid_request_id}", response_model=list[AuditLogResponse])
def get_audit_logs_for_aid_request(
    aid_request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    return (
        db.query(AuditLog)
        .filter(AuditLog.aid_request_id == aid_request_id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )