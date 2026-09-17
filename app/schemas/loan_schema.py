from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class LoanStatus(str, Enum):
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"


class LoanBase(BaseModel):
    user_id: int
    device_id: int
    status: LoanStatus = LoanStatus.ACTIVE


class LoanCreate(LoanBase):
    pass


class LoanUpdate(BaseModel):
    status: LoanStatus | None = None
    return_date: datetime | None = None


class LoanResponse(LoanBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    loan_date: datetime
    return_date: datetime | None = None


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str


class DeviceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    serial_number: str
    device_type: str


class LoanDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: LoanStatus
    loan_date: datetime
    return_date: datetime | None = None
    user: UserSummary
    device: DeviceSummary
