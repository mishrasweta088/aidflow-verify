from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db, require_roles
from app.models.aid_request import AidRequest, AidRequestStatus
from app.models.user import User, UserRole
from app.models.verification_task import VerificationTask, VerificationTaskStatus
from app.schemas.verification_task import VerificationTaskResponse, VerificationTaskUpdate

router = APIRouter(prefix="/verification-tasks", tags=["verification tasks"])


@router.get("/my", response_model=list[VerificationTaskResponse])
def get_my_verification_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.VOLUNTEER)),
):
    return (
        db.query(VerificationTask)
        .filter(VerificationTask.volunteer_id == current_user.id)
        .order_by(VerificationTask.created_at.desc())
        .all()
    )


@router.post("/{task_id}/verify", response_model=VerificationTaskResponse)
def verify_task(
    task_id: str,
    payload: VerificationTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.VOLUNTEER)),
):
    task = db.query(VerificationTask).filter(VerificationTask.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification task not found",
        )

    if task.volunteer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This task is not assigned to you",
        )

    aid_request = db.query(AidRequest).filter(AidRequest.id == task.aid_request_id).first()

    task.status = VerificationTaskStatus.VERIFIED
    task.notes = payload.notes
    aid_request.status = AidRequestStatus.VERIFIED

    db.commit()
    db.refresh(task)

    return task


@router.post("/{task_id}/reject", response_model=VerificationTaskResponse)
def reject_task(
    task_id: str,
    payload: VerificationTaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.VOLUNTEER)),
):
    task = db.query(VerificationTask).filter(VerificationTask.id == task_id).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification task not found",
        )

    if task.volunteer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This task is not assigned to you",
        )

    aid_request = db.query(AidRequest).filter(AidRequest.id == task.aid_request_id).first()

    task.status = VerificationTaskStatus.REJECTED
    task.notes = payload.notes
    aid_request.status = AidRequestStatus.VERIFICATION_REJECTED

    db.commit()
    db.refresh(task)

    return task