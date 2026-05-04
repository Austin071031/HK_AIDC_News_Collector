from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from hk_aidc_news.clustering.service import run_daily_clustering
from hk_aidc_news.db import get_session
from hk_aidc_news.discovery.service import run_daily_discovery
from hk_aidc_news.enrichment.service import run_daily_enrichment
from hk_aidc_news.ingestion.service import run_daily_ingestion

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/run-daily", status_code=202)
async def run_daily(db_session: Session = Depends(get_session)) -> dict[str, str]:
    try:
        discovered = await run_daily_discovery()
        ingested = run_daily_ingestion(discovered, db_session)
        enriched = await run_daily_enrichment(ingested, db_session)
        run_daily_clustering(enriched, db_session)
        db_session.commit()
        return {"status": "accepted"}
    except Exception:
        db_session.rollback()
        raise
