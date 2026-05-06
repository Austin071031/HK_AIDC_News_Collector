from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from hk_aidc_news.models.search_keyword import SearchKeyword
from hk_aidc_news.models.source import Source

def test_create_keyword(client: TestClient) -> None:
    response = client.post(
        "/api/keywords",
        json={"keyword": "AI Data Center", "active": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["keyword"] == "AI Data Center"
    assert data["id"] is not None

def test_get_keywords(client: TestClient, db_session: Session) -> None:
    keyword = SearchKeyword(keyword="Test Keyword")
    db_session.add(keyword)
    db_session.commit()

    response = client.get("/api/keywords")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(k["keyword"] == "Test Keyword" for k in data)

def test_delete_keyword(client: TestClient, db_session: Session) -> None:
    keyword = SearchKeyword(keyword="To Be Deleted")
    db_session.add(keyword)
    db_session.commit()
    db_session.refresh(keyword)

    response = client.delete(f"/api/keywords/{keyword.id}")
    assert response.status_code == 200

    deleted = db_session.query(SearchKeyword).filter(SearchKeyword.id == keyword.id).first()
    assert deleted is None

def test_create_source(client: TestClient) -> None:
    response = client.post(
        "/api/sources",
        json={
            "name": "API Test Source",
            "base_url": "https://example.com",
            "rss_url": "https://example.com/rss",
            "region": "hong_kong",
            "language": "en",
            "source_type": "news",
            "discovery_mode": "rss",
            "priority": 1,
            "active": True
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "API Test Source"
    assert data["rss_url"] == "https://example.com/rss"
    assert data["id"] is not None

def test_get_sources(client: TestClient, db_session: Session) -> None:
    source = Source(
        name="Get Test Source",
        base_url="https://get.example.com",
        region="hong_kong",
        language="en",
        source_type="news",
        discovery_mode="rss"
    )
    db_session.add(source)
    db_session.commit()

    response = client.get("/api/sources")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(s["name"] == "Get Test Source" for s in data)

def test_update_source(client: TestClient, db_session: Session) -> None:
    source = Source(
        name="Update Test Source",
        base_url="https://update.example.com",
        region="hong_kong",
        language="en",
        source_type="news",
        discovery_mode="rss"
    )
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)

    response = client.put(
        f"/api/sources/{source.id}",
        json={
            "name": "Updated Source Name",
            "base_url": "https://update.example.com",
            "rss_url": "https://update.example.com/rss",
            "region": "hong_kong",
            "language": "en",
            "source_type": "news",
            "discovery_mode": "rss",
            "priority": 2,
            "active": False
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Source Name"
    assert data["rss_url"] == "https://update.example.com/rss"
    assert data["priority"] == 2
    assert data["active"] is False

def test_delete_source(client: TestClient, db_session: Session) -> None:
    source = Source(
        name="Delete Test Source",
        base_url="https://delete.example.com",
        region="hong_kong",
        language="en",
        source_type="news",
        discovery_mode="rss"
    )
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)

    response = client.delete(f"/api/sources/{source.id}")
    assert response.status_code == 200

    deleted = db_session.query(Source).filter(Source.id == source.id).first()
    assert deleted is None
