import pytest

from hk_aidc_news.discovery.schemas import DiscoveryCandidate
from hk_aidc_news.discovery.service import DiscoveryService


class StubCollector:
    def __init__(self, candidates: list[DiscoveryCandidate]) -> None:
        self._candidates = candidates

    async def collect(self) -> list[DiscoveryCandidate]:
        return self._candidates


@pytest.mark.asyncio
async def test_discovery_service_merges_and_deduplicates_candidates() -> None:
    left = StubCollector(
        [
            DiscoveryCandidate(
                url="https://example.com/a",
                title="A",
                source_name="Left",
                discovered_via="rss",
            )
        ]
    )
    right = StubCollector(
        [
            DiscoveryCandidate(
                url="https://example.com/a?utm_source=newsletter",
                title="A copy",
                source_name="Right",
                discovered_via="firecrawl",
            ),
            DiscoveryCandidate(
                url="https://example.com/b",
                title="B",
                source_name="Right",
                discovered_via="firecrawl",
            ),
        ]
    )

    service = DiscoveryService([left, right])

    results = await service.collect()

    assert [item.url for item in results] == [
        "https://example.com/a",
        "https://example.com/b",
    ]
