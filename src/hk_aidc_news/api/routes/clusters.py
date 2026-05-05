from datetime import date
from typing import Any

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
    region: str | None = None,
    language: str | None = None,
    source_type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    relevance: str | None = None,
    analyst_status: str | None = None,
    topic_tag: str | None = None,
    db: Session = Depends(get_session),
) -> dict[str, list[dict[str, Any]]]:
    stmt = select(Cluster)
    
    needs_join = any([region, language, source_type, start_date, end_date, relevance, analyst_status, topic_tag])
    
    if needs_join:
        stmt = stmt.join(ClusterItem, Cluster.id == ClusterItem.cluster_id)
        stmt = stmt.join(RawDocument, ClusterItem.raw_document_id == RawDocument.id)
        
        if relevance or topic_tag:
            stmt = stmt.join(EnrichmentRecord, EnrichmentRecord.raw_document_id == RawDocument.id)
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
            enrichment = db.scalars(select(EnrichmentRecord).where(EnrichmentRecord.raw_document_id == first_item.raw_document_id)).first()
            raw_doc = db.scalars(select(RawDocument).where(RawDocument.id == first_item.raw_document_id)).first()
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
def get_cluster(cluster_id: int, db: Session = Depends(get_session)) -> dict[str, Any]:
    cluster = db.get(Cluster, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
        
    # In a real app we'd fetch related items, but for now we just return the skeleton
    items_in_db = db.scalars(select(ClusterItem).where(ClusterItem.cluster_id == cluster_id)).all()
    
    return {
        "id": cluster.id,
        "cluster_id": cluster.cluster_key,
        "headline": cluster.headline,
        "items": [{"id": item.id, "raw_document_id": item.raw_document_id} for item in items_in_db]
    }

