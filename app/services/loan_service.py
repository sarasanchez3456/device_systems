from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.loan_schema import LoanCreate, LoanStatus


def create_loan(db: Session, data: LoanCreate, user: User, device: Device) -> Loan:
    if data.status is not LoanStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New loans must have active status",
        )
    loan = Loan(user_id=user.id, device_id=device.id, status=LoanStatus.ACTIVE.value)
    db.add(loan)
    device.is_available = False
    db.commit()
    db.refresh(loan)
    return loan


def return_loan(db: Session, loan: Loan) -> Loan:
    if loan.status == LoanStatus.RETURNED.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The loan has already been returned",
        )
    loan.status = LoanStatus.RETURNED.value
    loan.return_date = datetime.now(timezone.utc)
    loan.device.is_available = True
    db.commit()
    db.refresh(loan)
    return loan
