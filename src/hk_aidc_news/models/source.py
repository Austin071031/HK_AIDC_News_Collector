from dataclasses import dataclass


@dataclass(slots=True)
class SourceDefinition:
    name: str
    base_url: str
    region: str
    language: str
    source_type: str
    discovery_mode: str
    priority: int
    active: bool = True
