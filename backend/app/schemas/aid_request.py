from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.aid_request import AidRequestStatus


class AidRequestCreate(BaseModel):
    title: str
    description: str
    category: str
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    
class AidRequestProofSubmit(BaseModel):
    proof_url: str
    proof_notes: str | None = None  


class AidRequestResponse(BaseModel):
    id: UUID
    requester_id: UUID
    title: str
    description: str
    category: str
    address: str | None
    latitude: float | None
    longitude: float | None
    status: AidRequestStatus

    ai_summary: str | None
    ai_urgency: str | None
    ai_missing_fields: str | None
    ai_risk_indicators: str | None
    ai_verification_checklist: str | None

    claimed_by_donor_id: UUID | None
    claimed_at: datetime | None
    
    proof_url: str | None
    proof_notes: str | None
    proof_uploaded_at: datetime | None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NearbyVolunteerResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    latitude: float
    longitude: float
    distance_meters: float