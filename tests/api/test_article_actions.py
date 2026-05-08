from datetime import datetime, timezone

from hk_aidc_news.models.source import Source
from hk_aidc_news.models.article import Article
from hk_aidc_news.models.raw_document import RawDocument

def test_create_article_action(client, db_session) -> None:
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

    # Add an article
    article = Article(
        raw_document_id=raw_doc.id,
        title="Test Article 1",
        url="https://test.com/article1",
        source_id=source.id
    )
    db_session.add(article)
    db_session.commit()

    # Call the API
    payload = {"is_hidden": True, "is_favorite": False, "notes": "Test note", "tags": ["test"]}
    response = client.post(f"/api/articles/{article.id}/actions", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "ok"
    
    # Check that it actually created the action
    from hk_aidc_news.models.analyst_action import AnalystAction
    from sqlalchemy import select
    
    action = db_session.scalar(select(AnalystAction).where(AnalystAction.article_id == article.id))
    assert action is not None
    assert action.is_hidden is True
    assert action.is_favorite is False
    assert action.notes == "Test note"
    assert action.tags == "test"
