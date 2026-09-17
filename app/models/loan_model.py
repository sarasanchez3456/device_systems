from __future__ import annotations

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    loan_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), nullable=False, default="active")

    user = relationship("User", back_populates="loans")
    device = relationship("Device", back_populates="loans")
