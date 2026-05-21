from unittest.mock import patch, MagicMock

from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from hk_aidc_news.app import create_app
from hk_aidc_news.models.source import Source
from hk_aidc_news.models.article import Article

def test_run_daily_job_dispatch() -> None:
    app = create_app()
    client = TestClient(app)
    
    # We expect the worker function `run_daily_pipeline_task` to be defined in `hk_aidc_news.worker`
    # and used in `hk_aidc_news.api.routes.jobs`.
    # Let's mock it at the place where it is used (jobs router).
    with patch("hk_aidc_news.api.routes.jobs.run_daily_pipeline_task") as mock_task:
        response = client.post("/api/jobs/run-rss-pipeline")
        
        assert response.status_code == 202
        assert response.json() == {"status": "accepted"}
        
        # In FastAPI TestClient, BackgroundTasks run synchronously after the response is sent.
        mock_task.assert_called_once()

def test_cleanup_database(client: TestClient, db_session: Session):
    # Add a mock article and source to ensure article is deleted and source is kept
    source = Source(
        name="Test Source", 
        base_url="http://test",
        region="global",
        language="en",
        source_type="rss",
        discovery_mode="rss"
    )
    db_session.add(source)
    db_session.commit()
    
    from hk_aidc_news.models.raw_document import RawDocument
    raw_doc = RawDocument(
        url="http://test/1", 
        canonical_url="http://test/1",
        title="Test Article",
        source_name="Test Source",
        discovered_via="rss",
        raw_html="<html></html>", 
        raw_text="text",
        crawled_at="now"
    )
    db_session.add(raw_doc)
    db_session.commit()
    
    article = Article(title="Test Article", source_id=source.id, url="http://test/1", raw_document_id=raw_doc.id)
    db_session.add(article)
    db_session.commit()

    assert db_session.query(Article).count() == 1
    assert db_session.query(Source).count() == 1

    response = client.post("/api/jobs/cleanup")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    assert db_session.query(Article).count() == 0
    assert db_session.query(Source).count() == 1
