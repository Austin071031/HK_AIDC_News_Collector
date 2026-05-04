from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from hk_aidc_news.clustering.service import run_daily_clustering
from hk_aidc_news.db import get_session
from hk_aidc_news.discovery.service import run_daily_discovery
from hk_aidc_news.enrichment.service import run_daily_enrichment, EnrichmentService
from hk_aidc_news.ingestion.service import run_daily_ingestion
from hk_aidc_news.discovery.firecrawl import FirecrawlCollector
from hk_aidc_news.llm.client import OpenAiCompatibleLlmClient

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

from hk_aidc_news.config import Settings

def get_settings() -> Settings:
    return Settings()

@router.post("/run-daily", status_code=202)
async def run_daily(
    settings: Settings = Depends(get_settings),
    db_session: Session = Depends(get_session)
) -> dict[str, str]:
    # Initialize clients
    firecrawl_collector = FirecrawlCollector(
        api_key=settings.firecrawl_api_key,
        base_url=settings.firecrawl_base_url,
    )
    
    llm_client = OpenAiCompatibleLlmClient(
        api_key=settings.openai_api_key,
        model=settings.llm_model,
    )
    enrichment_service = EnrichmentService(llm_client)

    try:
        discovered = await run_daily_discovery(collectors=[firecrawl_collector])
        ingested = run_daily_ingestion(discovered, db_session)
        enriched = await run_daily_enrichment(
            documents=ingested,
            enrichment_service=enrichment_service,
            model_name=settings.llm_model,
            db_session=db_session
        )
        run_daily_clustering(enriched, db_session)
        db_session.commit()
        return {"status": "accepted"}
    except Exception:
        db_session.rollback()
        raise
