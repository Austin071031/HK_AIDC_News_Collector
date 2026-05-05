import datetime
from unittest.mock import patch, MagicMock

import pytest

from hk_aidc_news.worker import run_daily_pipeline_task
from hk_aidc_news.models.source import Source
from hk_aidc_news.config import Settings

@pytest.fixture
def mock_db_session():
    with patch("hk_aidc_news.worker.session_factory") as mock_session_factory:
        mock_session = MagicMock()
        mock_session_factory.return_value.__enter__.return_value = mock_session
        yield mock_session

@pytest.mark.asyncio
async def test_worker_respects_priority_for_frequency(mock_db_session):
    # Setup sources with different priorities
    s1 = Source(name="high_priority", base_url="http://high.com", discovery_mode="rss", priority=1, active=True)
    s2 = Source(name="med_priority", base_url="http://med.com", discovery_mode="rss", priority=2, active=True)
    s3 = Source(name="low_priority", base_url="http://low.com", discovery_mode="rss", priority=3, active=True)
    
    mock_query = mock_db_session.query.return_value
    mock_filter = mock_query.filter.return_value
    mock_order = mock_filter.order_by.return_value
    # worker might just use filter(...).all() if it wasn't ordering, but we will mock both
    # so we mock .all() on mock_filter too just in case.
    mock_filter.all.return_value = [s1, s2, s3]
    mock_order.all.return_value = [s1, s2, s3]

    settings = Settings(firecrawl_api_key="test", openai_api_key="test")
    
    # Mock datetime to a specific day of year
    with patch("hk_aidc_news.worker.datetime") as mock_datetime:
        # Day 2 of the year
        mock_date = MagicMock()
        mock_date.timetuple.return_value.tm_yday = 2
        mock_datetime.datetime.now.return_value = mock_date
        
        with patch("hk_aidc_news.worker.RssCollector") as mock_rss_collector, \
             patch("hk_aidc_news.worker.FirecrawlCollector"), \
             patch("hk_aidc_news.worker.OpenAiCompatibleLlmClient"), \
             patch("hk_aidc_news.worker.EnrichmentService"), \
             patch("hk_aidc_news.worker.run_daily_discovery", return_value=[]), \
             patch("hk_aidc_news.worker.run_daily_ingestion", return_value=[]), \
             patch("hk_aidc_news.worker.run_daily_enrichment", return_value=[]), \
             patch("hk_aidc_news.worker.run_daily_clustering"):
             
            await run_daily_pipeline_task(settings)
            
            # On day 2, priority 1 (2 % 1 == 0) and priority 2 (2 % 2 == 0) should be included.
            # priority 3 (2 % 3 != 0) should be excluded.
            mock_rss_collector.assert_called_once()
            args, kwargs = mock_rss_collector.call_args
            feeds = kwargs.get("feeds", {})
            assert "high_priority" in feeds
            assert "med_priority" in feeds
            assert "low_priority" not in feeds
