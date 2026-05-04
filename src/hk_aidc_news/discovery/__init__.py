"""Discovery layer for collecting candidate article URLs."""

from hk_aidc_news.discovery.schemas import DiscoveryCandidate
from hk_aidc_news.discovery.service import DiscoveryService, canonicalize_url

__all__ = ["DiscoveryCandidate", "DiscoveryService", "canonicalize_url"]
