from sqlalchemy.orm import Session
from hk_aidc_news.models.cluster import Cluster, ClusterItem

def cluster_articles(articles: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}

    for article in articles:
        key = article.get("semantic_key") or article.get("canonical_url", "")
        bucket = grouped.setdefault(
            key,
            {
                "cluster_key": key,
                "headline": article.get("title", ""),
                "items": [],
            },
        )
        bucket["items"].append(article)

    return list(grouped.values())


def run_daily_clustering(
    articles: list[dict],
    db_session: Session | None = None,
) -> list[dict]:
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
