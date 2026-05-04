from collections.abc import Iterable
from datetime import UTC, datetime
from sqlalchemy.orm import Session

from hk_aidc_news.discovery.schemas import DiscoveryCandidate
from hk_aidc_news.ingestion.extractor import extract_text
from hk_aidc_news.ingestion.prefilter import is_viable_candidate
from hk_aidc_news.models.raw_document import RawDocument


def normalize_candidate(
    candidate: DiscoveryCandidate, raw_html: str
) -> dict[str, str]:
    return {
        "url": candidate.url,
        "canonical_url": candidate.url,
        "title": candidate.title,
        "source_name": candidate.source_name,
        "discovered_via": candidate.discovered_via,
        "raw_html": raw_html,
        "raw_text": extract_text(raw_html),
        "crawled_at": datetime.now(UTC).isoformat(),
    }


def run_daily_ingestion(
    candidates: Iterable[DiscoveryCandidate],
    db_session: Session | None = None,
) -> list[dict]:
    normalized = (normalize_candidate(candidate, "") for candidate in candidates)
    viable = [doc for doc in normalized if is_viable_candidate(doc)]
    
    if db_session:
        for doc in viable:
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
                db_session.commit()
                doc["id"] = rd.id
            else:
                doc["id"] = existing.id
                
    return viable
