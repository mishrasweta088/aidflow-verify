import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class VerificationTaskStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    VERIFIED = "verified"
    REJECTED = "rejected"


class VerificationTask(Base):
    __tablename__ = "verification_tasks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    aid_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("aid_requests.id"),
        nullable=False,
        index=True,
    )

    volunteer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[VerificationTaskStatus] = mapped_column(
        Enum(VerificationTaskStatus, name="verification_task_status"),
        default=VerificationTaskStatus.ASSIGNED,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

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

    aid_request = relationship("AidRequest")
    volunteer = relationship("User")
