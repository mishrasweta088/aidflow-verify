from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.verification_task import VerificationTaskStatus


class VerificationTaskAssign(BaseModel):
    volunteer_id: UUID


class VerificationTaskResponse(BaseModel):
    id: UUID
    aid_request_id: UUID
    volunteer_id: UUID
    status: VerificationTaskStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}