import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hk_aidc_news.models.base import Base
from hk_aidc_news.models.source import Source
from hk_aidc_news.models.search_keyword import SearchKeyword
import scripts.migrate_db as migrate_db

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, TestingSessionLocal

def test_seeding_empty_db(test_db):
    engine, session_factory = test_db
    
    # Run the seeding logic directly
    migrate_db.seed_data(session_factory)
    
    with session_factory() as session:
        sources = session.query(Source).all()
        assert len(sources) == 1
        assert sources[0].name == "Data Center Dynamics APAC"
        
        keywords = session.query(SearchKeyword).all()
        assert len(keywords) == 1
        assert keywords[0].keyword == "Hong Kong AI data center"

def test_seeding_non_empty_db(test_db):
    engine, session_factory = test_db
    
    # Pre-populate DB
    with session_factory() as session:
        session.add(Source(name="Existing", base_url="x", region="x", language="x", source_type="x", discovery_mode="x"))
        session.add(SearchKeyword(keyword="Existing Keyword"))
        session.commit()
        
    # Run seeding
    migrate_db.seed_data(session_factory)
    
    # Verify no new data was added
    with session_factory() as session:
        sources = session.query(Source).all()
        assert len(sources) == 1
        assert sources[0].name == "Existing"
        
        keywords = session.query(SearchKeyword).all()
        assert len(keywords) == 1
        assert keywords[0].keyword == "Existing Keyword"