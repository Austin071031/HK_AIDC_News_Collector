from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from hk_aidc_news.db import get_session
from hk_aidc_news.models.article import Article
from hk_aidc_news.models.analyst_action import AnalystAction

router = APIRouter(prefix="/api/articles", tags=["articles"])

class ActionPayload(BaseModel):
    is_hidden: bool = False
    is_favorite: bool = False
    notes: Optional[str] = None
    tags: Optional[list] = None

@router.post("/{article_id}/actions")
def submit_article_action(
    article_id: int, 
    payload: ActionPayload, 
    db: Session = Depends(get_session)
) -> dict:
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
        
    action = db.scalar(select(AnalystAction).where(AnalystAction.article_id == article_id))
    if not action:
        action = AnalystAction(article_id=article_id)
        db.add(action)
        
    action.is_hidden = payload.is_hidden
    action.is_favorite = payload.is_favorite
    action.notes = payload.notes
    action.tags = ",".join(payload.tags) if payload.tags else ""
    
    db.commit()
    
    return {"status": "ok"}
