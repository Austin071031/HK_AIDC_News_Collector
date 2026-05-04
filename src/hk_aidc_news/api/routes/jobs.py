from fastapi import APIRouter, Depends, BackgroundTasks

from hk_aidc_news.config import Settings
from hk_aidc_news.worker import run_daily_pipeline_task

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

def get_settings() -> Settings:
    return Settings()

@router.post("/run-daily", status_code=202)
async def run_daily(
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    background_tasks.add_task(run_daily_pipeline_task, settings)
    return {"status": "accepted"}

