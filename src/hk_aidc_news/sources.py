from pathlib import Path

import yaml

from hk_aidc_news.models.source import SourceDefinition


def load_sources(path: Path) -> list[SourceDefinition]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [SourceDefinition(**item) for item in payload["sources"]]
