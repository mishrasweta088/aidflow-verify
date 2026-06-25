from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: UUID
    aid_request_id: UUID
    actor_user_id: UUID
    action: str
    old_status: str | None
    new_status: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}