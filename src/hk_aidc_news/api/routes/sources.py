from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

from hk_aidc_news.db import get_session
from hk_aidc_news.models.source import Source

router = APIRouter(prefix="/api/sources", tags=["sources"])

class SourceBase(BaseModel):
    name: str
    base_url: str
    rss_url: Optional[str] = None
    region: str
    language: str
    source_type: str
    discovery_mode: str
    priority: int = 1
    active: bool = True

class SourceResponse(SourceBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

@router.get("", response_model=List[SourceResponse])
def get_sources(db: Session = Depends(get_session)):
    return db.query(Source).all()

@router.post("", response_model=SourceResponse)
def create_source(item: SourceBase, db: Session = Depends(get_session)):
    db_item = Source(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{source_id}", response_model=SourceResponse)
def update_source(source_id: int, item: SourceBase, db: Session = Depends(get_session)):
    db_item = db.query(Source).filter(Source.id == source_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Source not found")
    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_session)):
    db_item = db.query(Source).filter(Source.id == source_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Source not found")
    db.delete(db_item)
    db.commit()
    return {"status": "deleted"}
