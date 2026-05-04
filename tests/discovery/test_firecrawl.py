import pytest
import httpx
from unittest.mock import AsyncMock, patch

from hk_aidc_news.discovery.firecrawl import FirecrawlCollector


@pytest.mark.asyncio
async def test_firecrawl_collector_fetches_from_api():
    collector = FirecrawlCollector(api_key="test_key")

    mock_response = httpx.Response(
        200,
        json={
            "success": True,
            "data": [
                {
                    "url": "https://example.com/ai-dc",
                    "title": "New AI DC",
                }
            ]
        },
        request=httpx.Request("POST", "https://api.firecrawl.dev/v1/search")
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response
        
        results = await collector.collect()
        
        assert len(results) == 1
        assert results[0].url == "https://example.com/ai-dc"
        assert results[0].title == "New AI DC"
        assert results[0].source_name == "firecrawl"
        
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert args[0] == "/v1/search"
        assert kwargs["headers"]["Authorization"] == "Bearer test_key"
        assert "query" in kwargs["json"]
