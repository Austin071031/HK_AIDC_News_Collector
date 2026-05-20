import logging
import datetime
from hk_aidc_news.config import Settings
from hk_aidc_news.db import session_factory
from hk_aidc_news.clustering.service import run_daily_clustering
from hk_aidc_news.discovery.service import run_daily_discovery
from hk_aidc_news.enrichment.service import run_daily_enrichment, EnrichmentService
from hk_aidc_news.ingestion.service import run_daily_ingestion
from hk_aidc_news.discovery.firecrawl import FirecrawlCollector
from hk_aidc_news.discovery.rss import RssCollector
from hk_aidc_news.llm.client import OpenAiCompatibleLlmClient
from hk_aidc_news.models.source import Source
from hk_aidc_news.models.search_keyword import SearchKeyword

logger = logging.getLogger(__name__)

async def run_daily_pipeline_task(settings: Settings) -> None:
    logger.info("Starting daily pipeline task")
    
    with session_factory() as db_session:
        try:
            active_sources = (
                db_session.query(Source)
                .filter(Source.active == True)
                .order_by(Source.priority.asc())
                .all()
            )
            
            day_of_year = datetime.datetime.now().timetuple().tm_yday
            
            rss_feeds = {}
            for source in active_sources:
                if day_of_year % max(1, source.priority) != 0:
                    logger.info(f"Skipping source {source.name} due to priority {source.priority} on day {day_of_year}")
                    continue
                
                if source.discovery_mode == "rss":
                    if getattr(source, "rss_url", None):
                        rss_url = source.rss_url
                    else:
                        rss_url = source.base_url if source.base_url.endswith(".xml") else f"{source.base_url.rstrip('/')}/rss"
                    rss_feeds[source.name] = rss_url
            
            rss_collector = RssCollector(feeds=rss_feeds)
            
            active_keywords = db_session.query(SearchKeyword).filter(SearchKeyword.active == True).all()
            queries = [k.keyword for k in active_keywords]
            if not queries:
                queries = ["Hong Kong AI data center"]
            
            firecrawl_collector = FirecrawlCollector(
                api_key=settings.firecrawl_api_key,
                base_url=settings.firecrawl_base_url,
                queries=queries,
                limit=settings.default_query_limit,
            )
            
            # The user might provide a Deepseek API key instead of OpenAI.
            # Determine base_url and correct api_key based on configuration.
            import os
            
            # Use deepseek base URL if the model starts with "deepseek"
            base_url = None
            api_key = settings.openai_api_key or settings.llm_api_key
            if settings.llm_model.startswith("deepseek"):
                base_url = "https://api.deepseek.com/v1"
            
            llm_client = OpenAiCompatibleLlmClient(
                api_key=api_key,
                model=settings.llm_model,
                base_url=base_url
            )
            enrichment_service = EnrichmentService(llm_client)

            logger.info("Running discovery...")
            discovered = await run_daily_discovery(collectors=[firecrawl_collector, rss_collector])
            logger.info(f"Discovered {len(discovered)} items.")
            
            logger.info("Running ingestion...")
            ingested = run_daily_ingestion(discovered, db_session, settings=settings)
            logger.info(f"Ingested {len(ingested)} new documents.")
            
            logger.info("Running enrichment...")
            enriched = await run_daily_enrichment(
                documents=ingested,
                enrichment_service=enrichment_service,
                model_name=settings.llm_model,
                db_session=db_session
            )
            logger.info(f"Enriched {len(enriched)} items.")
            
            logger.info("Running clustering...")
            run_daily_clustering(enriched, db_session)
            
            db_session.commit()
            logger.info("Daily pipeline task completed successfully")
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error in daily pipeline task: {e}")
            raise
