import asyncio
import logging
from collections.abc import Iterable

import feedparser
import httpx

from hk_aidc_news.discovery.schemas import DiscoveryCandidate

logger = logging.getLogger(__name__)

class RssCollector:
    def __init__(self, feeds: dict[str, str]) -> None:
        """
        feeds: A mapping of source_name to RSS feed URL
        """
        self.feeds = feeds

    async def _fetch_feed(self, client: httpx.AsyncClient, source_name: str, url: str) -> list[DiscoveryCandidate]:
        try:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            parsed = feedparser.parse(response.text)
            
            candidates = []
            for entry in parsed.entries:
                # Basic validation
                if not hasattr(entry, "link") or not hasattr(entry, "title"):
                    continue
                    
                candidates.append(
                    DiscoveryCandidate(
                        url=entry.link,
                        title=entry.title,
                        source_name=source_name,
                        discovered_via="rss"
                    )
                )
            return candidates
        except Exception as e:
            logger.error(f"Error fetching RSS feed for {source_name} at {url}: {e}")
            return []

    async def collect(self) -> list[DiscoveryCandidate]:
        candidates = []
        async with httpx.AsyncClient() as client:
            tasks = [
                self._fetch_feed(client, source_name, url)
                for source_name, url in self.feeds.items()
            ]
            results = await asyncio.gather(*tasks)
            for result in results:
                candidates.extend(result)
        return candidates
