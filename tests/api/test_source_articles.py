from datetime import datetime, timezone

from hk_aidc_news.models.source import Source
from hk_aidc_news.models.article import Article
from hk_aidc_news.models.raw_document import RawDocument
from hk_aidc_news.models.enrichment import EnrichmentRecord
from hk_aidc_news.models.analyst_action import AnalystAction

def test_get_source_articles(client, db_session) -> None:
    # Add a source
    source = Source(
        name="Test Source Articles",
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
        source_name="Test Source Articles",
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
    
    # Add enrichment
    enrichment = EnrichmentRecord(
        article_id=article.id,
        summary="Test summary",
        relevance="high",
        confidence=0.9,
        rationale="test rationale",
        tags=["test"],
        entities=["test entity"],
        semantic_key="test_key",
        model_name="test_model"
    )
    db_session.add(enrichment)
    db_session.commit()
    
    # Add action
    action = AnalystAction(
        article_id=article.id,
        is_hidden=False,
        is_favorite=True,
        notes="Test note",
        tags="action_test"
    )
    db_session.add(action)
    db_session.commit()

    # Call the API
    response = client.get(f"/api/sources/{source.id}/articles")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    
    assert "title" in data[0]
    assert data[0]["title"] == "Test Article 1"
    assert "url" in data[0]
    
    # Should include enrichment data
    assert "enrichment" in data[0]
    assert data[0]["enrichment"]["summary"] == "Test summary"
    
    # Should include action data
    assert "action" in data[0]
    assert data[0]["action"]["is_favorite"] == True
