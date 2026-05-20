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

@router.get("")
def get_articles(
    region: Optional[str] = None,
    relevance: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    topic_tag: Optional[str] = None,
    analyst_status: Optional[str] = None,
    db: Session = Depends(get_session)
):
    from hk_aidc_news.models.source import Source
    from hk_aidc_news.models.enrichment import EnrichmentRecord

    stmt = (
        select(Article, EnrichmentRecord, Source)
        .outerjoin(EnrichmentRecord, Article.id == EnrichmentRecord.article_id)
        .join(Source, Article.source_id == Source.id)
    )
    
    if region:
        stmt = stmt.where(Source.region == region)
    if relevance:
        stmt = stmt.where(EnrichmentRecord.relevance == relevance)
    if topic_tag:
        stmt = stmt.where(EnrichmentRecord.tags.ilike(f"%{topic_tag}%"))
    if start_date:
        stmt = stmt.where(Article.published_at >= start_date)
    if end_date:
        stmt = stmt.where(Article.published_at <= end_date)
        
    stmt = stmt.order_by(Article.published_at.desc().nullslast())
    
    # Optional limit to avoid loading too many
    stmt = stmt.limit(200)
    
    results = db.execute(stmt).all()
    
    articles = []
    for article, enrichment, source in results:
        article_dict = {c.name: getattr(article, c.name) for c in article.__table__.columns}
        
        article_dict["source_name"] = source.name
        article_dict["source_region"] = source.region

        if enrichment:
            article_dict["enrichment"] = {
                "summary": enrichment.summary,
                "relevance": enrichment.relevance,
                "tags": enrichment.tags
            }
        else:
            article_dict["enrichment"] = None
            
        articles.append(article_dict)
        
    return articles

@router.get("/{article_id}/content")
def get_article_content(article_id: int, db: Session = Depends(get_session)):
    from hk_aidc_news.models.raw_document import RawDocument
    
    article = db.get(Article, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
        
    raw_doc = db.get(RawDocument, article.raw_document_id)
    if not raw_doc:
        raise HTTPException(status_code=404, detail="Raw document not found")
        
    return {
        "raw_text": raw_doc.raw_text,
        "raw_html": raw_doc.raw_html
    }

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
