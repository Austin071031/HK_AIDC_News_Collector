from fastapi import APIRouter

from hk_aidc_news.clustering.service import run_daily_clustering
from hk_aidc_news.discovery.service import run_daily_discovery
from hk_aidc_news.enrichment.service import run_daily_enrichment
from hk_aidc_news.ingestion.service import run_daily_ingestion

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/run-daily", status_code=202)
async def run_daily() -> dict[str, str]:
    discovered = await run_daily_discovery()
    ingested = run_daily_ingestion(discovered)
    enriched = await run_daily_enrichment(ingested)
    run_daily_clustering(enriched)
    return {"status": "accepted"}
