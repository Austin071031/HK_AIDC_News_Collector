from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse

from hk_aidc_news.config import Settings
from hk_aidc_news.worker import run_daily_pipeline_task
from hk_aidc_news.log_stream import setup_log_stream, log_generator

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

def get_settings() -> Settings:
    return Settings()

@router.post("/run-daily", status_code=202)
def run_daily(
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
) -> dict:
    setup_log_stream()
    background_tasks.add_task(run_daily_pipeline_task, settings)
    return {"status": "accepted"}

@router.get("/stream")
async def stream_logs():
    setup_log_stream()
    return StreamingResponse(log_generator(), media_type="text/event-stream")

