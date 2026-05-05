from collections.abc import Iterable
from typing import Protocol, List, Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from hk_aidc_news.discovery.schemas import DiscoveryCandidate


class DiscoveryCollector(Protocol):
    async def collect(self) -> List[DiscoveryCandidate]:
        ...

def canonicalize_url(url: str) -> str:
    parts = urlsplit(url)
    filtered_query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if not key.startswith("utm_")
    ]
    return urlunsplit(
        (parts.scheme, parts.netloc, parts.path, urlencode(filtered_query), "")
    )


class DiscoveryService:
    def __init__(self, collectors: Iterable) -> None:
        self.collectors = list(collectors)

    async def collect(self) -> List[DiscoveryCandidate]:
        seen: set = set()
        merged: List[DiscoveryCandidate] = []

        for collector in self.collectors:
            for item in await collector.collect():
                canonical_url = canonicalize_url(item.url)
                if canonical_url in seen:
                    continue

                seen.add(canonical_url)
                merged.append(
                    DiscoveryCandidate(
                        url=canonical_url,
                        title=item.title,
                        source_name=item.source_name,
                        discovered_via=item.discovered_via,
                    )
                )

        return merged


async def run_daily_discovery(
    collectors: Optional[Iterable] = None,
) -> List[DiscoveryCandidate]:
    return await DiscoveryService(collectors or []).collect()
