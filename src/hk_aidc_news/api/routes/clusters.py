from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, and_, or_, String
from sqlalchemy.orm import Session

from hk_aidc_news.db import get_session
from hk_aidc_news.models.cluster import Cluster, ClusterItem
from hk_aidc_news.models.enrichment import EnrichmentRecord
from hk_aidc_news.models.raw_document import RawDocument
from hk_aidc_news.models.source import Source
from hk_aidc_news.models.analyst_action import AnalystAction

router = APIRouter(prefix="/api/clusters", tags=["clusters"])

@router.get("")
def list_clusters(
    region: Optional[str] = None,
    language: Optional[str] = None,
    source_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    relevance: Optional[str] = None,
    analyst_status: Optional[str] = None,
    topic_tag: Optional[str] = None,
    db: Session = Depends(get_session),
) -> dict:
    stmt = select(Cluster)
    
    needs_join = any([region, language, source_type, start_date, end_date, relevance, analyst_status, topic_tag])
    
    if needs_join:
        stmt = stmt.join(ClusterItem, Cluster.id == ClusterItem.cluster_id)
        from hk_aidc_news.models.article import Article
        stmt = stmt.join(Article, ClusterItem.article_id == Article.id)
        stmt = stmt.join(RawDocument, Article.raw_document_id == RawDocument.id)
        
        if relevance or topic_tag:
            stmt = stmt.join(EnrichmentRecord, EnrichmentRecord.article_id == Article.id)
            if relevance:
                stmt = stmt.where(EnrichmentRecord.relevance == relevance)
            # Filter by topic tag
            if topic_tag:
                # JSON contains check (simple string search for SQLite fallback)
                # In PostgreSQL we'd use .contains(), but for simple strings LIKE works as a fallback
                stmt = stmt.where(func.cast(EnrichmentRecord.tags, String).like(f"%{topic_tag}%"))
            
        if region or language or source_type:
            stmt = stmt.join(Source, Source.name == RawDocument.source_name)
            if region:
                stmt = stmt.where(Source.region == region)
            if language:
                stmt = stmt.where(Source.language == language)
            if source_type:
                stmt = stmt.where(Source.source_type == source_type)
                
        if start_date:
            stmt = stmt.where(RawDocument.crawled_at >= start_date.isoformat())
        if end_date:
            stmt = stmt.where(RawDocument.crawled_at <= end_date.isoformat() + "T23:59:59")
            
        if analyst_status:
            stmt = stmt.outerjoin(AnalystAction, AnalystAction.cluster_id == Cluster.id)
            if analyst_status == "hidden":
                stmt = stmt.where(AnalystAction.is_hidden == True)
            elif analyst_status == "favorite":
                stmt = stmt.where(AnalystAction.is_favorite == True)
            elif analyst_status == "unread":
                stmt = stmt.where(or_(AnalystAction.id == None, and_(AnalystAction.is_hidden == False, AnalystAction.is_favorite == False)))
        else:
            # Default behavior: exclude hidden clusters
            stmt = stmt.outerjoin(AnalystAction, AnalystAction.cluster_id == Cluster.id)
            stmt = stmt.where(or_(AnalystAction.id == None, AnalystAction.is_hidden == False))
            
        stmt = stmt.distinct()

    clusters = db.scalars(stmt).all()
    
    items = []
    for c in clusters:
        # Load cluster items
        c_items = db.scalars(select(ClusterItem).where(ClusterItem.cluster_id == c.id)).all()
        source_count = len(c_items)
        
        # Load enrichment for the first item to get summary/tags
        first_item = c_items[0] if c_items else None
        summary = ""
        topic_tags = []
        extracted_entities = []
        publish_date = None
        region_str = ""
        
        if first_item:
            from hk_aidc_news.models.article import Article
            enrichment = db.scalars(select(EnrichmentRecord).where(EnrichmentRecord.article_id == first_item.article_id)).first()
            article = db.scalars(select(Article).where(Article.id == first_item.article_id)).first()
            raw_doc = db.scalars(select(RawDocument).where(RawDocument.id == article.raw_document_id)).first() if article else None
            if enrichment:
                summary = enrichment.summary
                topic_tags = enrichment.tags
                extracted_entities = enrichment.entities
            if raw_doc:
                publish_date = raw_doc.crawled_at
                source_record = db.scalars(select(Source).where(Source.name == raw_doc.source_name)).first()
                if source_record:
                    region_str = source_record.region

        items.append({
            "cluster_id": c.id,
            "headline": c.headline,
            "summary": summary,
            "topic_tags": topic_tags,
            "extracted_entities": extracted_entities,
            "publish_date": publish_date,
            "source_count": source_count,
            "region": region_str,
        })
        
    return {"items": items}

@router.get("/{cluster_id}")
def get_cluster(cluster_id: int, db: Session = Depends(get_session)) -> dict:
    cluster = db.get(Cluster, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
        
    items_in_db = db.scalars(select(ClusterItem).where(ClusterItem.cluster_id == cluster_id)).all()
    
    rationale = ""
    extracted_entities = []
    articles = []
    
    for item in items_in_db:
        if not item.article_id:
            continue
            
        from hk_aidc_news.models.article import Article
        article = db.get(Article, item.article_id)
        if not article:
            continue
            
        raw_doc = db.get(RawDocument, article.raw_document_id)
        if not raw_doc:
            continue
            
        enrichment = db.scalars(select(EnrichmentRecord).where(EnrichmentRecord.article_id == article.id)).first()
        
        # Grab rationale and entities from the first item that has them
        if enrichment and not rationale:
            rationale = enrichment.rationale
            extracted_entities = enrichment.entities
            
        articles.append({
            "id": raw_doc.id,
            "title": raw_doc.title,
            "url": raw_doc.url,
            "source_name": raw_doc.source_name,
            "crawled_at": raw_doc.crawled_at
        })
    
    return {
        "id": cluster.id,
        "cluster_id": cluster.cluster_key,
        "headline": cluster.headline,
        "rationale": rationale,
        "extracted_entities": extracted_entities,
        "articles": articles
    }

