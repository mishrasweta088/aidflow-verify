from sqlalchemy import func
from app.models.profile import Profile
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.aid_request import AidRequest, AidRequestStatus
from app.services.ai_review import generate_ai_review

from app.dependencies import get_current_user, get_db, require_roles
from app.models.user import User, UserRole
from app.schemas.aid_request import AidRequestCreate, AidRequestResponse, NearbyVolunteerResponse

from app.models.verification_task import VerificationTask
from app.schemas.verification_task import VerificationTaskAssign, VerificationTaskResponse

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

@router.get(
    "/{aid_request_id}/nearby-volunteers",
    response_model=list[NearbyVolunteerResponse],
)
def get_nearby_volunteers(
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

    if aid_request.latitude is None or aid_request.longitude is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aid request does not have location coordinates",
        )

    distance_meters = func.ST_DistanceSphere(
        func.ST_MakePoint(Profile.longitude, Profile.latitude),
        func.ST_MakePoint(aid_request.longitude, aid_request.latitude),
    )

    results = (
        db.query(
            User.id,
            User.email,
            Profile.full_name,
            Profile.latitude,
            Profile.longitude,
            distance_meters.label("distance_meters"),
        )
        .join(Profile, Profile.user_id == User.id)
        .filter(User.role == UserRole.VOLUNTEER)
        .filter(Profile.latitude.isnot(None))
        .filter(Profile.longitude.isnot(None))
        .order_by(distance_meters)
        .limit(10)
        .all()
    )

    return results

@router.post(
    "/{aid_request_id}/assign-volunteer",
    response_model=VerificationTaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_volunteer_to_aid_request(
    aid_request_id: str,
    payload: VerificationTaskAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    aid_request = db.query(AidRequest).filter(AidRequest.id == aid_request_id).first()

    if not aid_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aid request not found",
        )

    if aid_request.status != AidRequestStatus.ADMIN_APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aid request must be admin approved before volunteer assignment",
        )

    volunteer = (
        db.query(User)
        .filter(User.id == payload.volunteer_id)
        .filter(User.role == UserRole.VOLUNTEER)
        .first()
    )

    if not volunteer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Volunteer not found",
        )

    verification_task = VerificationTask(
        aid_request_id=aid_request.id,
        volunteer_id=volunteer.id,
    )

    aid_request.status = AidRequestStatus.ASSIGNED_TO_VOLUNTEER

    db.add(verification_task)
    db.commit()
    db.refresh(verification_task)

    return verification_task