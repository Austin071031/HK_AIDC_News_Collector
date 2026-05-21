from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List

from hk_aidc_news.db import get_session
from hk_aidc_news.models.system_config import SystemConfig

router = APIRouter(prefix="/api/config", tags=["config"])

class ConfigUpdate(BaseModel):
    value: str

class ConfigResponse(BaseModel):
    key: str
    value: str | None
    model_config = ConfigDict(from_attributes=True)

@router.get("", response_model=List[ConfigResponse])
def get_configs(db: Session = Depends(get_session)):
    return db.query(SystemConfig).all()

@router.get("/{key}", response_model=ConfigResponse)
def get_config(key: str, db: Session = Depends(get_session)):
    db_item = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Config not found")
    return db_item

@router.put("/{key}", response_model=ConfigResponse)
def update_config(key: str, item: ConfigUpdate, db: Session = Depends(get_session)):
    db_item = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not db_item:
        # Create it if it doesn't exist
        db_item = SystemConfig(key=key, value=item.value)
        db.add(db_item)
    else:
        db_item.value = item.value
    
    db.commit()
    db.refresh(db_item)
    return db_item
