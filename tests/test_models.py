import pytest
from sqlalchemy.orm import Session
from hk_aidc_news.models.source import Source
from hk_aidc_news.models.search_keyword import SearchKeyword
from hk_aidc_news.models.base import Base

def test_source_rss_url(db_session: Session) -> None:
    # Test that a Source can be created with an rss_url
    source = Source(
        name="Test RSS Source",
        base_url="https://example.com",
        rss_url="https://example.com/rss",
        region="hong_kong",
        language="en",
        source_type="news",
        discovery_mode="rss"
    )
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)
    
    assert source.id is not None
    assert source.rss_url == "https://example.com/rss"
    
def test_source_rss_url_nullable(db_session: Session) -> None:
    # Test that a Source can be created without an rss_url
    source = Source(
        name="Test Non-RSS Source",
        base_url="https://example.com/other",
        region="hong_kong",
        language="en",
        source_type="news",
        discovery_mode="firecrawl"
    )
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)
    
    assert source.id is not None
    assert source.rss_url is None

def test_search_keyword_creation(db_session: Session) -> None:
    # Test creating a SearchKeyword
    keyword = SearchKeyword(keyword="Hong Kong AI data center")
    db_session.add(keyword)
    db_session.commit()
    db_session.refresh(keyword)
    
    assert keyword.id is not None
    assert keyword.keyword == "Hong Kong AI data center"
    assert keyword.active is True

def test_search_keyword_unique(db_session: Session) -> None:
    # Test that keywords must be unique
    from sqlalchemy.exc import IntegrityError
    
    keyword1 = SearchKeyword(keyword="Duplicate")
    db_session.add(keyword1)
    db_session.commit()
    
    keyword2 = SearchKeyword(keyword="Duplicate")
    db_session.add(keyword2)
    with pytest.raises(IntegrityError):
        db_session.commit()
