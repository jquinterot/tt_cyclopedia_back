from fastapi import Depends
from sqlalchemy.orm import Session
from app.config.postgres_config import get_db
from .models import Equipment
from .exceptions import EquipmentNotFound


def valid_equipment_id(equipment_id: str, db: Session = Depends(get_db)) -> Equipment:
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        raise EquipmentNotFound()
    return equipment
