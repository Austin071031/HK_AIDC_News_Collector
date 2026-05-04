from dataclasses import dataclass


@dataclass(slots=True)
class DiscoveryCandidate:
    url: str
    title: str
    source_name: str
    discovered_via: str
