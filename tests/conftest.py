import pytest
from fastapi.testclient import TestClient

from hk_aidc_news.app import create_app
from hk_aidc_news.db import get_session
from hk_aidc_news.models.base import Base
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