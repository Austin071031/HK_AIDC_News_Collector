from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import delete

from hk_aidc_news.config import Settings
from hk_aidc_news.worker import run_daily_pipeline_task
from hk_aidc_news.log_stream import setup_log_stream, log_generator
from hk_aidc_news.db import get_session
from hk_aidc_news.models import (
    AnalystAction,
    ClusterItem,
    Cluster,
    EnrichmentRecord,
    Article,
    RawDocument,
    DiscoveryJob
)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

def get_settings() -> Settings:
    return Settings()

@router.post("/run-daily", status_code=202)
async def run_daily(
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
) -> dict:
    setup_log_stream()
    background_tasks.add_task(run_daily_pipeline_task, settings)
    return {"status": "accepted"}

@router.post("/cleanup", status_code=200)
def cleanup_database(db: Session = Depends(get_session)) -> dict:
    """
    Cleans up all news content from the database but leaves sources and keywords intact.
    """
    # Delete in order of foreign key dependencies (child -> parent)
    db.execute(delete(AnalystAction))
    db.execute(delete(ClusterItem))
    db.execute(delete(Cluster))
    db.execute(delete(EnrichmentRecord))
    db.execute(delete(Article))
    db.execute(delete(RawDocument))
    db.execute(delete(DiscoveryJob))
    
    db.commit()
    return {"status": "ok", "message": "Content database cleaned up successfully"}

@router.get("/stream")
async def stream_logs():
    setup_log_stream()
    return StreamingResponse(log_generator(), media_type="text/event-stream")

