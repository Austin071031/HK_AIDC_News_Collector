from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List

from hk_aidc_news.db import get_session
from hk_aidc_news.models.search_keyword import SearchKeyword

router = APIRouter(prefix="/api/keywords", tags=["keywords"])

class KeywordCreate(BaseModel):
    keyword: str
    active: bool = True

class KeywordResponse(KeywordCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)

@router.get("", response_model=List[KeywordResponse])
def get_keywords(db: Session = Depends(get_session)):
    return db.query(SearchKeyword).all()

@router.post("", response_model=KeywordResponse)
def create_keyword(item: KeywordCreate, db: Session = Depends(get_session)):
    db_item = SearchKeyword(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{keyword_id}")
def delete_keyword(keyword_id: int, db: Session = Depends(get_session)):
    db_item = db.query(SearchKeyword).filter(SearchKeyword.id == keyword_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Keyword not found")
    db.delete(db_item)
    db.commit()
    return {"status": "deleted"}
