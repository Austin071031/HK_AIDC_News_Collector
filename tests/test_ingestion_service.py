from unittest.mock import patch, AsyncMock
import pytest

from hk_aidc_news.discovery.schemas import DiscoveryCandidate
from hk_aidc_news.ingestion.extractor import extract_text
from hk_aidc_news.ingestion.service import normalize_candidate


def test_extract_text_strips_html() -> None:
    html = (
        "<html><body><h1>GPU campus</h1>"
        "<p>New AI data center announced.</p></body></html>"
    )

    assert extract_text(html) == "GPU campus New AI data center announced."


def test_normalize_candidate_builds_raw_document_payload() -> None:
    candidate = DiscoveryCandidate(
        url="https://example.com/a",
        title="A",
        source_name="Example",
        discovered_via="rss",
    )

    payload = normalize_candidate(candidate, "<p>Hello world</p>")

    assert payload["canonical_url"] == "https://example.com/a"
    assert payload["source_name"] == "Example"
    assert payload["raw_text"] == "Hello world"


@pytest.mark.asyncio
async def test_run_daily_ingestion_partial_failure(monkeypatch) -> None:
    from hk_aidc_news.ingestion.service import run_daily_ingestion

    c1 = DiscoveryCandidate(url="http://example.com/fail", title="Fail", source_name="src", discovered_via="rss")
    c2 = DiscoveryCandidate(url="http://example.com/pass", title="Pass", source_name="src", discovered_via="rss")

    def mock_normalize(candidate, html):
        if "fail" in candidate.url:
            raise RuntimeError("extraction failed")
        return {
            "url": candidate.url,
            "canonical_url": candidate.url,
            "title": candidate.title,
            "source_name": candidate.source_name,
            "discovered_via": candidate.discovered_via,
            "raw_html": html,
            "raw_text": "Long enough text to pass the prefilter about data centers and ai GPUs... " * 5,
            "crawled_at": "2024-01-01T00:00:00Z"
        }

    monkeypatch.setattr("hk_aidc_news.ingestion.service.normalize_candidate", mock_normalize)

    # run_daily_ingestion should continue despite the first one raising an error
    results = await run_daily_ingestion([c1, c2])
    
    assert len(results) == 1
    assert results[0]["url"] == "http://example.com/pass"

