from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.device_model import Device
from app.models.loan_model import Loan
from app.models.user_model import User
from app.schemas.loan_schema import LoanCreate, LoanDetailResponse, LoanResponse, LoanStatus, LoanUpdate
from app.services.device_service import find_device
from app.services.loan_service import create_loan as create_loan_service, return_loan as return_loan_service
from app.services.user_service import find_user

router = APIRouter()
history_router = APIRouter()
ERROR_RESPONSES = {
    404: {"description": "The requested loan, user or device was not found."},
    409: {"description": "The business rule prevents this operation."},
    422: {"description": "Validation error."},
}


@router.get("", response_model=list[LoanDetailResponse], summary="List loans", description="Retrieve loans with advanced filters by status, user email, device type, or date.", response_description="Loans matching the filters.", responses={422: ERROR_RESPONSES[422]})
def list_loans(
    status: LoanStatus | None = Query(default=None, description="Filter by loan status."),
    user_email: str | None = Query(default=None, description="Filter by user email."),
    device_type: str | None = Query(default=None, description="Filter by device type."),
    loan_date_from: datetime | None = Query(default=None, description="Include loans created on or after this date."),
    loan_date_to: datetime | None = Query(default=None, description="Include loans created on or before this date."),
    return_date_from: datetime | None = Query(default=None, description="Include returns on or after this date."),
    return_date_to: datetime | None = Query(default=None, description="Include returns on or before this date."),
    db: Session = Depends(get_db),
):
    query = db.query(Loan).join(User, Loan.user_id == User.id).join(Device, Loan.device_id == Device.id)
    if status:
        query = query.filter(Loan.status == status.value)
    if user_email:
        query = query.filter(User.email.ilike(f"%{user_email}%"))
    if device_type:
        query = query.filter(Device.device_type.ilike(f"%{device_type}%"))
    if loan_date_from:
        query = query.filter(Loan.loan_date >= loan_date_from)
    if loan_date_to:
        query = query.filter(Loan.loan_date <= loan_date_to)
    if return_date_from:
        query = query.filter(Loan.return_date >= return_date_from)
    if return_date_to:
        query = query.filter(Loan.return_date <= return_date_to)
    loans = query.order_by(Loan.id).all()
    return [
        LoanDetailResponse(
            id=loan.id,
            status=loan.status,
            loan_date=loan.loan_date,
            return_date=loan.return_date,
            user={"id": loan.user.id, "name": loan.user.name, "email": loan.user.email},
            device={
                "id": loan.device.id,
                "name": loan.device.name,
                "serial_number": loan.device.serial_number,
                "device_type": loan.device.device_type,
            },
        )
        for loan in loans
    ]


@router.get("/details", response_model=list[LoanDetailResponse], summary="List detailed loans", response_description="Loans including user and device information.", responses={422: ERROR_RESPONSES[422]})
def list_loans_details(db: Session = Depends(get_db)):
    loans = db.query(Loan).join(User).join(Device).all()
    return [
        LoanDetailResponse(
            id=loan.id,
            status=loan.status,
            loan_date=loan.loan_date,
            return_date=loan.return_date,
            user={"id": loan.user.id, "name": loan.user.name, "email": loan.user.email},
            device={
                "id": loan.device.id,
                "name": loan.device.name,
                "serial_number": loan.device.serial_number,
                "device_type": loan.device.device_type,
            },
        )
        for loan in loans
    ]


@router.get("/{loan_id}", response_model=LoanResponse, summary="Get loan by ID", response_description="The requested loan.", responses=ERROR_RESPONSES)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return loan


@router.get("/{loan_id}/details", response_model=LoanDetailResponse, summary="Get loan details", response_description="The loan with user and device information.", responses=ERROR_RESPONSES)
def get_loan_details(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(Loan).join(User).join(Device).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return LoanDetailResponse(
        id=loan.id,
        status=loan.status,
        loan_date=loan.loan_date,
        return_date=loan.return_date,
        user={"id": loan.user.id, "name": loan.user.name, "email": loan.user.email},
        device={
            "id": loan.device.id,
            "name": loan.device.name,
            "serial_number": loan.device.serial_number,
            "device_type": loan.device.device_type,
        },
    )


@router.get("/user/{user_id}", response_model=list[LoanDetailResponse], summary="Get loans for user", response_description="The user's loan history.", responses=ERROR_RESPONSES)
def get_user_loans(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    loans = db.query(Loan).join(User).join(Device).filter(Loan.user_id == user_id).all()
    return [
        LoanDetailResponse(
            id=loan.id,
            status=loan.status,
            loan_date=loan.loan_date,
            return_date=loan.return_date,
            user={"id": loan.user.id, "name": loan.user.name, "email": loan.user.email},
            device={
                "id": loan.device.id,
                "name": loan.device.name,
                "serial_number": loan.device.serial_number,
                "device_type": loan.device.device_type,
            },
        )
        for loan in loans
    ]


@router.get("/device/{device_id}", response_model=list[LoanDetailResponse], summary="Get loans for device", response_description="The device's loan history.", responses=ERROR_RESPONSES)
def get_device_loans(device_id: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    loans = db.query(Loan).join(User).join(Device).filter(Loan.device_id == device_id).all()
    return [
        LoanDetailResponse(
            id=loan.id,
            status=loan.status,
            loan_date=loan.loan_date,
            return_date=loan.return_date,
            user={"id": loan.user.id, "name": loan.user.name, "email": loan.user.email},
            device={
                "id": loan.device.id,
                "name": loan.device.name,
                "serial_number": loan.device.serial_number,
                "device_type": loan.device.device_type,
            },
        )
        for loan in loans
    ]


@history_router.get("/users/{user_id}/loans", response_model=list[LoanDetailResponse], summary="Get loans for user", response_description="The user's loan history.", responses=ERROR_RESPONSES)
def get_user_loans_alias(user_id: int, db: Session = Depends(get_db)):
    return get_user_loans(user_id, db)


@history_router.get("/devices/{device_id}/loans", response_model=list[LoanDetailResponse], summary="Get loans for device", response_description="The device's loan history.", responses=ERROR_RESPONSES)
def get_device_loans_alias(device_id: int, db: Session = Depends(get_db)):
    return get_device_loans(device_id, db)


@router.post("", response_model=LoanResponse, status_code=status.HTTP_201_CREATED, summary="Create loan", response_description="The created loan.", responses=ERROR_RESPONSES)
def create_loan(loan: LoanCreate, db: Session = Depends(get_db)):
    user = find_user(db, loan.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    device = find_device(db, loan.device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    if not device.is_available:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Device is not available")
    return create_loan_service(db, loan, user, device)


@router.patch("/{loan_id}", response_model=LoanResponse, summary="Update loan", response_description="The updated loan.", responses=ERROR_RESPONSES)
def update_loan(loan_id: int, loan: LoanUpdate, db: Session = Depends(get_db)):
    db_loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not db_loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    update_data = loan.model_dump(exclude_unset=True)
    if update_data.get("status") == LoanStatus.RETURNED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Use the return endpoint to close a loan")
    if "status" in update_data:
        update_data["status"] = update_data["status"].value
    for field, value in update_data.items():
        setattr(db_loan, field, value)
    db.commit()
    db.refresh(db_loan)
    return db_loan


@router.patch("/{loan_id}/return", response_model=LoanResponse, summary="Return loan", response_description="The returned loan.", responses=ERROR_RESPONSES)
def return_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    return return_loan_service(db, loan)


@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete loan", response_description="The loan was deleted.", responses=ERROR_RESPONSES)
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Loan not found")
    db.delete(loan)
    db.commit()
    return None
