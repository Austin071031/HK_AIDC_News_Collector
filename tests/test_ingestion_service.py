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
