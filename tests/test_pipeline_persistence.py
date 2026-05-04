import pytest
from fastapi.testclient import TestClient

from hk_aidc_news.app import create_app
from hk_aidc_news.db import get_session
from hk_aidc_news.models.base import Base
from hk_aidc_news.models.raw_document import RawDocument
from hk_aidc_news.models.enrichment import EnrichmentRecord
from hk_aidc_news.models.cluster import Cluster, ClusterItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

@pytest.fixture(name="db_engine")
def fixture_db_engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:", 
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture(name="db_session_factory")
def fixture_db_session_factory(db_engine):
    return sessionmaker(
        bind=db_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        future=True,
    )

@pytest.fixture(name="db_session")
def fixture_db_session(db_session_factory):
    with db_session_factory() as session:
        yield session

@pytest.fixture(name="client")
def fixture_client(db_session):
    app = create_app()
    
    def override_get_session():
        yield db_session
        
    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)

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
