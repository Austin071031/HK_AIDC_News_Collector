import httpx
from typing import List
from hk_aidc_news.discovery.schemas import DiscoveryCandidate

class FirecrawlCollector:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.firecrawl.dev",
        query: str = "Hong Kong AI data center",
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.query = query

    async def collect(self) -> List[DiscoveryCandidate]:
        if not self.api_key:
            return []

        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                "/v1/search",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"query": self.query, "pageOptions": {"fetchPageContent": False}},
            )
            response.raise_for_status()
            data = response.json()

            candidates = []
            for item in data.get("data", []):
                candidates.append(
                    DiscoveryCandidate(
                        url=item.get("url", ""),
                        title=item.get("title", ""),
                        source_name="firecrawl",
                        discovered_via="firecrawl",
                    )
                )
            return candidates
