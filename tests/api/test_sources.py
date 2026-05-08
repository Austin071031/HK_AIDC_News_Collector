from datetime import datetime, timezone

from hk_aidc_news.models.source import Source
from hk_aidc_news.models.article import Article
from hk_aidc_news.models.raw_document import RawDocument

def test_get_sources_with_counts(client, db_session) -> None:
    # Add a source
    source = Source(
        name="Test Source",
        base_url="https://test.com",
        region="hong_kong",
        language="en",
        source_type="news",
        discovery_mode="rss"
    )
    db_session.add(source)
    db_session.commit()

    # Add a raw document
    raw_doc = RawDocument(
        url="https://test.com/article1",
        canonical_url="https://test.com/article1",
        title="Test Article 1",
        source_name="Test Source",
        discovered_via="rss",
        raw_html="<html></html>",
        raw_text="Test content",
        crawled_at=datetime.now(timezone.utc).isoformat()
    )
    db_session.add(raw_doc)
    db_session.commit()

    # Add an article linked to the source
    article = Article(
        raw_document_id=raw_doc.id,
        title="Test Article 1",
        url="https://test.com/article1",
        source_id=source.id
    )
    db_session.add(article)
    db_session.commit()

    # Call the API
    response = client.get("/api/sources?with_counts=true")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    
    assert "article_count" in data[0]
    assert data[0]["article_count"] == 1
