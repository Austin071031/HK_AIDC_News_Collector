import logging
from hk_aidc_news.config import Settings
from hk_aidc_news.db import session_factory
from hk_aidc_news.clustering.service import run_daily_clustering
from hk_aidc_news.discovery.service import run_daily_discovery
from hk_aidc_news.enrichment.service import run_daily_enrichment, EnrichmentService
from hk_aidc_news.ingestion.service import run_daily_ingestion
from hk_aidc_news.discovery.firecrawl import FirecrawlCollector
from hk_aidc_news.llm.client import OpenAiCompatibleLlmClient

logger = logging.getLogger(__name__)

async def run_daily_pipeline_task(settings: Settings) -> None:
    logger.info("Starting daily pipeline task")
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

    with session_factory() as db_session:
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
            logger.info("Daily pipeline task completed successfully")
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error in daily pipeline task: {e}")
            raise
