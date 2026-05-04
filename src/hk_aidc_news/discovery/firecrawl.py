from collections.abc import Awaitable, Callable

from hk_aidc_news.discovery.schemas import DiscoveryCandidate


class FirecrawlCollector:
    def __init__(
        self,
        fetch_candidates: Callable[[], Awaitable[list[DiscoveryCandidate]]],
    ) -> None:
        self._fetch_candidates = fetch_candidates

    async def collect(self) -> list[DiscoveryCandidate]:
        return await self._fetch_candidates()
