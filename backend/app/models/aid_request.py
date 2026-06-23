import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AidRequestStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    AI_REVIEWED = "ai_reviewed"
    ADMIN_APPROVED = "admin_approved"
    ADMIN_REJECTED = "admin_rejected"
    ASSIGNED_TO_VOLUNTEER = "assigned_to_volunteer"
    VERIFIED = "verified"
    VERIFICATION_REJECTED = "verification_rejected"
    CLAIMED = "claimed"
    FULFILLED = "fulfilled"


class AidRequest(Base):
    __tablename__ = "aid_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    requester_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)

    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    status: Mapped[AidRequestStatus] = mapped_column(
        Enum(AidRequestStatus, name="aid_request_status"),
        default=AidRequestStatus.SUBMITTED,
        nullable=False,
    )

    ai_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_urgency: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ai_missing_fields: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_risk_indicators: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_verification_checklist: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    requester = relationship("User")