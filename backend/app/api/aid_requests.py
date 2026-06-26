from sqlalchemy import func
from app.models.profile import Profile
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.aid_request import AidRequest, AidRequestStatus
from app.services.ai_review import generate_ai_review

from app.dependencies import get_current_user, get_db, require_roles
from app.models.user import User, UserRole

from app.models.verification_task import VerificationTask
from app.schemas.verification_task import VerificationTaskAssign, VerificationTaskResponse

from datetime import datetime

from app.schemas.aid_request import AidRequestCreate, AidRequestProofSubmit, AidRequestResponse, NearbyVolunteerResponse

from app.services.audit import create_audit_log

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

@router.get("/verified", response_model=list[AidRequestResponse])
def get_verified_aid_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.DONOR)),
):
    return (
        db.query(AidRequest)
        .filter(AidRequest.status == AidRequestStatus.VERIFIED)
        .order_by(AidRequest.created_at.desc())
        .all()
    )

@router.get("/admin/all", response_model=list[AidRequestResponse])
def get_all_aid_requests_for_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    return db.query(AidRequest).order_by(AidRequest.created_at.desc()).all()

@router.post("/{aid_request_id}/claim", response_model=AidRequestResponse)
def claim_aid_request(
    aid_request_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.DONOR)),
):
    aid_request = db.query(AidRequest).filter(AidRequest.id == aid_request_id).first()

    if not aid_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aid request not found",
        )

    if aid_request.status != AidRequestStatus.VERIFIED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only verified aid requests can be claimed",
        )

    if aid_request.claimed_by_donor_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Aid request is already claimed",
        )

    old_status = aid_request.status.value

    aid_request.claimed_by_donor_id = current_user.id
    aid_request.claimed_at = datetime.utcnow()
    aid_request.status = AidRequestStatus.CLAIMED

    create_audit_log(
        db=db,
        aid_request_id=aid_request.id,
        actor_user_id=current_user.id,
        action="donor_claimed_request",
        old_status=old_status,
        new_status=AidRequestStatus.CLAIMED.value,
        notes="Donor claimed aid request",
    )

    db.commit()
    db.refresh(aid_request)

    return aid_request

@router.post("/{aid_request_id}/submit-proof", response_model=AidRequestResponse)
def submit_fulfillment_proof(
    aid_request_id: str,
    payload: AidRequestProofSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.DONOR)),
):
    aid_request = db.query(AidRequest).filter(AidRequest.id == aid_request_id).first()

    if not aid_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aid request not found",
        )

    if aid_request.status != AidRequestStatus.CLAIMED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only claimed aid requests can receive proof",
        )

    if aid_request.claimed_by_donor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the donor who claimed this request can submit proof",
        )

    old_status = aid_request.status.value

    aid_request.proof_url = payload.proof_url
    aid_request.proof_notes = payload.proof_notes
    aid_request.proof_uploaded_at = datetime.utcnow()

    create_audit_log(
        db=db,
        aid_request_id=aid_request.id,
        actor_user_id=current_user.id,
        action="donor_submitted_proof",
        old_status=old_status,
        new_status=aid_request.status.value,
        notes="Donor submitted fulfillment proof",
    )

    db.commit()
    db.refresh(aid_request)

    return aid_request

@router.post("/{aid_request_id}/mark-fulfilled", response_model=AidRequestResponse)
def mark_aid_request_fulfilled(
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

    if aid_request.status != AidRequestStatus.CLAIMED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only claimed aid requests can be marked fulfilled",
        )

    if not aid_request.proof_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Proof must be submitted before marking fulfilled",
        )

    old_status = aid_request.status.value
    aid_request.status = AidRequestStatus.FULFILLED

    create_audit_log(
        db=db,
        aid_request_id=aid_request.id,
        actor_user_id=current_user.id,
        action="admin_marked_fulfilled",
        old_status=old_status,
        new_status=AidRequestStatus.FULFILLED.value,
        notes="Admin marked aid request as fulfilled",
    )

    db.commit()
    db.refresh(aid_request)

    return aid_request

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

    old_status = aid_request.status.value
    aid_request.status = AidRequestStatus.ADMIN_APPROVED

    create_audit_log(
        db=db,
        aid_request_id=aid_request.id,
        actor_user_id=current_user.id,
        action="admin_approved_request",
        old_status=old_status,
        new_status=AidRequestStatus.ADMIN_APPROVED.value,
        notes="Admin approved aid request",
    )

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

    old_status = aid_request.status.value
    aid_request.status = AidRequestStatus.ADMIN_REJECTED

    create_audit_log(
        db=db,
        aid_request_id=aid_request.id,
        actor_user_id=current_user.id,
        action="admin_rejected_request",
        old_status=old_status,
        new_status=AidRequestStatus.ADMIN_REJECTED.value,
        notes="Admin rejected aid request",
    )

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

    old_status = aid_request.status.value

    verification_task = VerificationTask(
        aid_request_id=aid_request.id,
        volunteer_id=volunteer.id,
    )

    aid_request.status = AidRequestStatus.ASSIGNED_TO_VOLUNTEER

    create_audit_log(
        db=db,
        aid_request_id=aid_request.id,
        actor_user_id=current_user.id,
        action="admin_assigned_volunteer",
        old_status=old_status,
        new_status=AidRequestStatus.ASSIGNED_TO_VOLUNTEER.value,
        notes=f"Admin assigned volunteer {volunteer.id}",
    )

    db.add(verification_task)
    db.commit()
    db.refresh(verification_task)

    return verification_task
