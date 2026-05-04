from collections.abc import Iterable
from datetime import UTC, datetime

from hk_aidc_news.discovery.schemas import DiscoveryCandidate
from hk_aidc_news.ingestion.extractor import extract_text
from hk_aidc_news.ingestion.prefilter import is_viable_candidate


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
) -> list[dict[str, str]]:
    normalized = (normalize_candidate(candidate, "") for candidate in candidates)
    return [doc for doc in normalized if is_viable_candidate(doc)]
