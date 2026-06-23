from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db, require_roles
from app.models.aid_request import AidRequest
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