from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import difflib

from hk_aidc_news.models.cluster import Cluster, ClusterItem

def calculate_similarity(title1: str, title2: str) -> float:
    if not title1 or not title2:
        return 0.0
    return difflib.SequenceMatcher(None, title1.lower(), title2.lower()).ratio()

def has_entity_overlap(entities1: List[str], entities2: set) -> bool:
    if not entities1 or not entities2:
        return False
    return len(set(e.lower() for e in entities1) & entities2) > 0

def cluster_articles(articles: List[Dict]) -> List[Dict]:
    clusters = []
    
    for doc in articles:
        semantic_key = doc.get("semantic_key", "")
        title = doc.get("title", "")
        entities = doc.get("entities", [])
        
        matched_cluster = None
        for cluster in clusters:
            # 1. Semantic Key Match
            if semantic_key and cluster["cluster_key"] == semantic_key:
                matched_cluster = cluster
                break
                
            # 2. Fuzzy Title Similarity + Entity Overlap
            # If titles are very similar and they share at least one entity, group them
            c_title = cluster["headline"]
            c_entities = cluster.get("entities", set())
            
            if calculate_similarity(title, c_title) > 0.75 and has_entity_overlap(entities, c_entities):
                matched_cluster = cluster
                break
                
        if matched_cluster:
            matched_cluster["items"].append(doc)
            # Add new entities to the cluster's set to improve future matches
            matched_cluster["entities"].update(e.lower() for e in entities)
        else:
            # Create a new cluster
            new_cluster_key = semantic_key or doc.get("canonical_url", doc.get("url", "unknown"))
            clusters.append({
                "cluster_key": new_cluster_key,
                "headline": title or "Untitled",
                "entities": set(e.lower() for e in entities),
                "items": [doc]
            })
            
    # Clean up the internal 'entities' set before returning
    for cluster in clusters:
        cluster.pop("entities", None)
        
    return clusters


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
                    article_id=item.get("article_id")
                ).first()
                if not existing_item:
                    ci = ClusterItem(
                        cluster_id=cluster_id,
                        article_id=item.get("article_id"),
                        reason="stub reason"
                    )
                    db_session.add(ci)
        db_session.flush()
        
    return clusters
