from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from hk_aidc_news.models.cluster import Cluster, ClusterItem

def cluster_articles(articles: List[Dict]) -> List[Dict]:
    clusters_map = {}
    for doc in articles:
        semantic_key = doc.get("semantic_key", doc.get("canonical_url", doc.get("url")))
        if not semantic_key:
            continue
            
        if semantic_key not in clusters_map:
            clusters_map[semantic_key] = {
                "cluster_key": semantic_key,
                "headline": doc.get("title", "Untitled"),
                "items": []
            }
            
        clusters_map[semantic_key]["items"].append(doc)
        
    return list(clusters_map.values())


def run_daily_clustering(
    articles: List[Dict],
    db_session: Optional[Session] = None,
) -> List[Dict]:
    clusters = cluster_articles(articles)
    
    if db_session:
        for c in clusters:
            existing = db_session.query(Cluster).filter_by(cluster_key=c["cluster_key"]).first()
            if not existing:
                cluster_model = Cluster(
                    cluster_key=c["cluster_key"],
                    headline=c["headline"]
                )
                db_session.add(cluster_model)
                db_session.flush()
                cluster_id = cluster_model.id
            else:
                cluster_id = existing.id
                
            for item in c["items"]:
                # To prevent duplicate cluster items if ran multiple times
                existing_item = db_session.query(ClusterItem).filter_by(
                    cluster_id=cluster_id, 
                    raw_document_id=item.get("id")
                ).first()
                if not existing_item:
                    ci = ClusterItem(
                        cluster_id=cluster_id,
                        raw_document_id=item.get("id"),
                        reason="stub reason"
                    )
                    db_session.add(ci)
        db_session.flush()
        
    return clusters
