from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.aid_request import AidRequest, AidRequestStatus
from app.services.ai_review import generate_ai_review

from app.dependencies import get_current_user, get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.aid_request import AidRequestCreate, AidRequestResponse

router = APIRouter(prefix="/aid-requests", tags=["aid requests"])


@router.post(
    "",
    response_model=AidRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_aid_request(
    payload: AidRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.REQUESTER)),
):
    aid_request = AidRequest(
        requester_id=current_user.id,
        title=payload.title,
        description=payload.description,
        category=payload.category,
        address=payload.address,
        latitude=payload.latitude,
        longitude=payload.longitude,
    )

    db.add(aid_request)
    db.commit()
    db.refresh(aid_request)

    return aid_request


@router.get("/my", response_model=list[AidRequestResponse])
def get_my_aid_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(AidRequest)
        .filter(AidRequest.requester_id == current_user.id)
        .order_by(AidRequest.created_at.desc())
        .all()
    )

@router.post("/{aid_request_id}/ai-review", response_model=AidRequestResponse)
def review_aid_request_with_ai(
    aid_request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    aid_request = db.query(AidRequest).filter(AidRequest.id == aid_request_id).first()

    if not aid_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aid request not found",
        )

    ai_review = generate_ai_review(aid_request)

    aid_request.ai_summary = ai_review["ai_summary"]
    aid_request.ai_urgency = ai_review["ai_urgency"]
    aid_request.ai_missing_fields = ai_review["ai_missing_fields"]
    aid_request.ai_risk_indicators = ai_review["ai_risk_indicators"]
    aid_request.ai_verification_checklist = ai_review["ai_verification_checklist"]
    aid_request.status = AidRequestStatus.AI_REVIEWED

    db.commit()
    db.refresh(aid_request)

    return aid_request

@router.post("/{aid_request_id}/approve", response_model=AidRequestResponse)
def approve_aid_request(
    aid_request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    aid_request = db.query(AidRequest).filter(AidRequest.id == aid_request_id).first()

    if not aid_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aid request not found",
        )

    aid_request.status = AidRequestStatus.ADMIN_APPROVED

    db.commit()
    db.refresh(aid_request)

    return aid_request


@router.post("/{aid_request_id}/reject", response_model=AidRequestResponse)
def reject_aid_request(
    aid_request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    aid_request = db.query(AidRequest).filter(AidRequest.id == aid_request_id).first()

    if not aid_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aid request not found",
        )

    aid_request.status = AidRequestStatus.ADMIN_REJECTED

    db.commit()
    db.refresh(aid_request)

    return aid_request