from unittest.mock import patch

from hk_aidc_news.models.cluster import Cluster
from hk_aidc_news.models.analyst_action import AnalystAction

def test_cluster_feed_endpoint_returns_items(client, db_session) -> None:
    # Add a mock cluster to the DB
    cluster = Cluster(cluster_key="test-cluster", headline="Test Headline")
    db_session.add(cluster)
    db_session.commit()

    response = client.get("/api/clusters")

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["headline"] == "Test Headline"
    assert items[0]["cluster_id"] == cluster.id

def test_cluster_feed_filtering(client, db_session) -> None:
    response = client.get("/api/clusters?region=hong_kong&relevance=direct")
    assert response.status_code == 200
    assert "items" in response.json()

def test_cluster_detail_endpoint(client, db_session) -> None:
    cluster = Cluster(cluster_key="test-detail", headline="Detail Headline")
    db_session.add(cluster)
    db_session.commit()

    response = client.get(f"/api/clusters/{cluster.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == cluster.id
    assert data["headline"] == "Detail Headline"
    assert "articles" in data

def test_cluster_actions_endpoint(client, db_session) -> None:
    cluster = Cluster(cluster_key="test-action", headline="Action Headline")
    db_session.add(cluster)
    db_session.commit()

    payload = {
        "is_hidden": True,
        "is_favorite": True,
        "notes": "Test notes",
        "tags": ["urgent", "review"]
    }
    response = client.post(f"/api/clusters/{cluster.id}/actions", json=payload)
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

    # Verify DB
    action = db_session.query(AnalystAction).filter_by(cluster_id=cluster.id).first()
    assert action is not None
    assert action.is_hidden is True
    assert action.is_favorite is True
    assert action.notes == "Test notes"
    assert "urgent,review" in action.tags

@patch("hk_aidc_news.api.routes.jobs.run_daily_pipeline_task")
def test_manual_run_endpoint_returns_accepted(mock_task, client) -> None:
    response = client.post("/api/jobs/run-daily")
    assert response.status_code == 202
    assert response.json()["status"] == "accepted"
    mock_task.assert_called_once()
