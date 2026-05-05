import pytest

from hk_aidc_news.models.raw_document import RawDocument
from hk_aidc_news.models.enrichment import EnrichmentRecord
from hk_aidc_news.models.cluster import Cluster

def test_daily_job_persists_records(client, db_session, db_session_factory, monkeypatch):
    from hk_aidc_news.discovery.schemas import DiscoveryCandidate
    
    # Mock the session_factory in the worker so it uses the test database
    monkeypatch.setattr("hk_aidc_news.worker.session_factory", db_session_factory)

    async def mock_discovery(*args, **kwargs):
        return [
            DiscoveryCandidate(
                url="https://example.com/test",
                title="Test Title",
                source_name="Test Source",
                discovered_via="test"
            )
        ]
        
    monkeypatch.setattr("hk_aidc_news.worker.run_daily_discovery", mock_discovery)

    monkeypatch.setattr("hk_aidc_news.ingestion.service.is_viable_candidate", lambda x: True)

    from hk_aidc_news.llm.schemas import EnrichmentResult
    async def mock_enrich(*args, **kwargs):
        return EnrichmentResult(
            relevance="direct",
            confidence=0.9,
            rationale="mock",
            tags=["mock"],
            entities=["mock"],
            summary="mock summary",
            semantic_key="mock-key"
        )
    monkeypatch.setattr("hk_aidc_news.llm.client.OpenAiCompatibleLlmClient.enrich", mock_enrich)

    response = client.post("/api/jobs/run-daily")
    assert response.status_code == 202
    
    # Verify records were added to the DB
    assert db_session.query(RawDocument).count() > 0
    assert db_session.query(EnrichmentRecord).count() > 0
    assert db_session.query(Cluster).count() > 0
