from fastapi.testclient import TestClient

from hk_aidc_news.app import create_app


def test_cluster_feed_endpoint_returns_items() -> None:
    client = TestClient(create_app())

    response = client.get("/api/clusters")

    assert response.status_code == 200
    assert response.json()["items"] == []


def test_manual_run_endpoint_returns_accepted() -> None:
    client = TestClient(create_app())

    response = client.post("/api/jobs/run-daily")

    assert response.status_code == 202
    assert response.json()["status"] == "accepted"
