from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

from hk_aidc_news.db import get_session
from hk_aidc_news.models.source import Source
from hk_aidc_news.models.article import Article

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
    article_count: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

@router.get("", response_model=List[SourceResponse])
def get_sources(
    with_counts: bool = Query(False),
    db: Session = Depends(get_session)
):
    if with_counts:
        stmt = (
            select(Source, func.count(Article.id).label("article_count"))
            .outerjoin(Article, Source.id == Article.source_id)
            .group_by(Source.id)
        )
        results = db.execute(stmt).all()
        
        sources = []
        for source, count in results:
            source_dict = {c.name: getattr(source, c.name) for c in source.__table__.columns}
            source_dict["article_count"] = count
            sources.append(source_dict)
        return sources

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
