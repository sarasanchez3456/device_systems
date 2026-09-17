from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.device_model import Device
from app.schemas.device_schema import DeviceCreate, DeviceReplace, DeviceResponse, DeviceUpdate
from app.services.device_service import serial_in_use

router = APIRouter()
ERROR_RESPONSES = {
    400: {"description": "The request conflicts with existing device data."},
    404: {"description": "Device not found."},
    422: {"description": "Validation error."},
}


@router.get("", response_model=list[DeviceResponse], summary="List devices", description="Available devices can be filtered by type, availability or brand.", response_description="Devices matching the filters.", responses={422: ERROR_RESPONSES[422]})
def list_devices(
    device_type: str | None = Query(default=None, description="Filter by device type."),
    is_available: bool | None = Query(default=None, description="Filter by availability."),
    brand: str | None = Query(default=None, description="Filter by brand."),
    search: str | None = Query(default=None, description="Search by name, serial number or brand."),
    db: Session = Depends(get_db),
):
    query = db.query(Device)
    if device_type:
        query = query.filter(Device.device_type.ilike(f"%{device_type}%"))
    if is_available is not None:
        query = query.filter(Device.is_available == is_available)
    if brand:
        query = query.filter(Device.brand.ilike(f"%{brand}%"))
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Device.name.ilike(search_term),
                Device.serial_number.ilike(search_term),
                Device.brand.ilike(search_term),
            )
        )
    return query.order_by(Device.id).all()


@router.get("/{device_id}", response_model=DeviceResponse, summary="Get device by ID", response_description="The requested device.", responses={404: ERROR_RESPONSES[404], 422: ERROR_RESPONSES[422]})
def get_device(device_id: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED, summary="Create device", response_description="The created device.", responses=ERROR_RESPONSES)
def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    if serial_in_use(db, device.serial_number):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device serial number already exists")
    new_device = Device(**device.model_dump())
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device


@router.put("/{device_id}", response_model=DeviceResponse, summary="Replace device", description="Replace all editable fields of an existing device.", response_description="The device was replaced successfully.", responses=ERROR_RESPONSES)
def update_device(device_id: int, device: DeviceReplace, db: Session = Depends(get_db)):
    db_device = db.query(Device).filter(Device.id == device_id).first()
    if not db_device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    update_data = device.model_dump(exclude_unset=True)
    if "serial_number" in update_data and update_data["serial_number"]:
        if serial_in_use(db, update_data["serial_number"], device_id):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Device serial number already exists")
    for field, value in update_data.items():
        setattr(db_device, field, value)
    db.commit()
    db.refresh(db_device)
    return db_device


@router.patch("/{device_id}", response_model=DeviceResponse, summary="Partial update device", response_description="The updated device.", responses=ERROR_RESPONSES)
def patch_device(device_id: int, device: DeviceUpdate, db: Session = Depends(get_db)):
    return update_device(device_id, device, db)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete device", response_description="The device was deleted.", responses={404: ERROR_RESPONSES[404], 422: ERROR_RESPONSES[422]})
def delete_device(device_id: int, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    db.delete(device)
    db.commit()
    return None
