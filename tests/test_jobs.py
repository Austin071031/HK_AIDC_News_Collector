from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from hk_aidc_news.app import create_app

def test_run_daily_job_dispatch() -> None:
    app = create_app()
    client = TestClient(app)
    
    # We expect the worker function `run_daily_pipeline_task` to be defined in `hk_aidc_news.worker`
    # and used in `hk_aidc_news.api.routes.jobs`.
    # Let's mock it at the place where it is used (jobs router).
    with patch("hk_aidc_news.api.routes.jobs.run_daily_pipeline_task") as mock_task:
        response = client.post("/api/jobs/run-daily")
        
        assert response.status_code == 202
        assert response.json() == {"status": "accepted"}
        
        # In FastAPI TestClient, BackgroundTasks run synchronously after the response is sent.
        mock_task.assert_called_once()
