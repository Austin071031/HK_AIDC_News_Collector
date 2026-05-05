from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from hk_aidc_news.db import get_session
from hk_aidc_news.models.cluster import Cluster, ClusterItem
from hk_aidc_news.models.enrichment import EnrichmentRecord
from hk_aidc_news.models.raw_document import RawDocument
from hk_aidc_news.models.source import Source

router = APIRouter(prefix="/api/clusters", tags=["clusters"])

@router.get("")
def list_clusters(
    region: str | None = None,
    language: str | None = None,
    source_type: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    relevance: str | None = None,
    db: Session = Depends(get_session),
) -> dict[str, list[dict[str, Any]]]:
    stmt = select(Cluster)
    
    # We can join ClusterItem, RawDocument, Source, EnrichmentRecord to filter
    # But since a cluster has multiple items, filtering means "clusters that have AT LEAST ONE item matching"
    # Let's do an EXISTS or just join and distinct
    
    needs_join = any([region, language, source_type, start_date, end_date, relevance])
    
    if needs_join:
        stmt = stmt.join(ClusterItem, Cluster.id == ClusterItem.cluster_id)
        stmt = stmt.join(RawDocument, ClusterItem.raw_document_id == RawDocument.id)
        
        # In this minimal setup, let's assume we match Source by source_name in RawDocument or Source table
        # Since Source table is newly added, we join it by matching names or via Article
        # Wait, the task says: Connect `GET /api/clusters` to the PostgreSQL database.
        # Implement filtering parameters (Region, Language, Source Type, Date Range, Relevance).
        # We can just join EnrichmentRecord on raw_document_id
        if relevance:
            stmt = stmt.join(EnrichmentRecord, EnrichmentRecord.raw_document_id == RawDocument.id)
            stmt = stmt.where(EnrichmentRecord.relevance == relevance)
            
        # To filter by Region, Language, Source Type, we need the Source model
        # Let's join Source on Source.name == RawDocument.source_name
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
            
        stmt = stmt.distinct()

    clusters = db.scalars(stmt).all()
    
    items = []
    for c in clusters:
        items.append({
            "cluster_id": c.id,
            "headline": c.headline,
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

