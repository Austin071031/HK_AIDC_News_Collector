from typing import Dict, List, Optional
from collections.abc import Iterable
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from hk_aidc_news.discovery.schemas import DiscoveryCandidate
from hk_aidc_news.ingestion.extractor import extract_text
from hk_aidc_news.ingestion.prefilter import is_viable_candidate
from hk_aidc_news.models.raw_document import RawDocument
from hk_aidc_news.models.article import Article
from hk_aidc_news.models.source import Source
from dateutil import parser


def normalize_candidate(
    candidate: DiscoveryCandidate, raw_html: str
) -> Dict:
    try:
        raw_text = extract_text(raw_html)
    except Exception:
        raw_text = ""

    return {
        "url": candidate.url,
        "canonical_url": candidate.url,
        "title": candidate.title,
        "source_name": candidate.source_name,
        "discovered_via": candidate.discovered_via,
        "raw_html": raw_html,
        "raw_text": raw_text,
        "crawled_at": datetime.now(timezone.utc).isoformat(),
    }


def run_daily_ingestion(
    candidates: Iterable,
    db_session: Optional[Session] = None,
) -> List[Dict]:
    normalized = []
    for candidate in candidates:
        try:
            doc = normalize_candidate(candidate, "")
            normalized.append(doc)
        except Exception:
            # Ensure it doesn't crash the pipeline but continue processing the rest
            continue

    viable = [doc for doc in normalized if is_viable_candidate(doc)]
    
    final_docs = []
    if db_session:
        for doc in viable:
            try:
                with db_session.begin_nested():
                    existing = db_session.query(RawDocument).filter_by(canonical_url=doc["canonical_url"]).first()
                    if not existing:
                        rd = RawDocument(
                            url=doc["url"],
                            canonical_url=doc["canonical_url"],
                            title=doc["title"],
                            source_name=doc["source_name"],
                            discovered_via=doc["discovered_via"],
                            raw_html=doc["raw_html"],
                            raw_text=doc["raw_text"],
                            crawled_at=doc["crawled_at"],
                        )
                        db_session.add(rd)
                        db_session.flush()
                        doc["id"] = rd.id
                        
                        # Create corresponding Article
                        source = db_session.query(Source).filter_by(name=doc["source_name"]).first()
                        source_id = source.id if source else None
                        
                        try:
                            published_at = parser.parse(doc["crawled_at"])
                        except Exception:
                            published_at = datetime.now(timezone.utc)
                            
                        article = Article(
                            raw_document_id=rd.id,
                            title=doc["title"],
                            url=doc["url"],
                            source_id=source_id,
                            published_at=published_at
                        )
                        db_session.add(article)
                        db_session.flush()
                        doc["article_id"] = article.id
                    else:
                        doc["id"] = existing.id
                        article = db_session.query(Article).filter_by(raw_document_id=existing.id).first()
                        if article:
                            doc["article_id"] = article.id
                        else:
                            # Fallback if article doesn't exist for some reason
                            source = db_session.query(Source).filter_by(name=doc["source_name"]).first()
                            try:
                                published_at = parser.parse(doc["crawled_at"])
                            except Exception:
                                published_at = datetime.now(timezone.utc)
                            article = Article(
                                raw_document_id=existing.id,
                                title=doc["title"],
                                url=doc["url"],
                                source_id=source.id if source else None,
                                published_at=published_at
                            )
                            db_session.add(article)
                            db_session.flush()
                            doc["article_id"] = article.id
                final_docs.append(doc)
            except Exception as e:
                continue
    else:
        final_docs = viable
                
    return final_docs
