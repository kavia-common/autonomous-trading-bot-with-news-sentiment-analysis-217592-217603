from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.db.models import ConfigItem
from src.db.session import get_db
from src.schemas import ConfigItemCreate, ConfigItemRead

router = APIRouter()


# PUBLIC_INTERFACE
@router.get("/", response_model=List[ConfigItemRead], summary="List configuration items")
def list_config(db: Session = Depends(get_db)):
    """
    List all configuration entries stored in the database.
    """
    return db.query(ConfigItem).all()


# PUBLIC_INTERFACE
@router.put("/", response_model=ConfigItemRead, summary="Upsert configuration item")
def upsert_config(payload: ConfigItemCreate, db: Session = Depends(get_db)):
    """
    Create or update a configuration item.

    Args:
        payload (ConfigItemCreate): key and value
    """
    item = db.query(ConfigItem).filter(ConfigItem.key == payload.key).first()
    if item:
        item.value = payload.value
        db.add(item)
    else:
        item = ConfigItem(key=payload.key, value=payload.value)
        db.add(item)
    db.commit()
    db.refresh(item)
    return item


# PUBLIC_INTERFACE
@router.delete("/{key}", summary="Delete configuration item")
def delete_config(key: str, db: Session = Depends(get_db)):
    """
    Delete a configuration item by key.
    """
    item = db.query(ConfigItem).filter(ConfigItem.key == key).first()
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return {"status": "deleted", "key": key}
