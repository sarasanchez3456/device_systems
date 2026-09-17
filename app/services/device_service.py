from sqlalchemy.orm import Session

from app.models.device_model import Device


def find_device(db: Session, device_id: int) -> Device | None:
    return db.query(Device).filter(Device.id == device_id).first()


def serial_in_use(db: Session, serial_number: str, device_id: int | None = None) -> bool:
    query = db.query(Device).filter(Device.serial_number == serial_number)
    if device_id is not None:
        query = query.filter(Device.id != device_id)
    return query.first() is not None
