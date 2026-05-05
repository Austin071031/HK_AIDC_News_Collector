from pathlib import Path

import yaml

from hk_aidc_news.models.source import Source


def load_sources(path: Path) -> list[Source]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [Source(**item) for item in payload["sources"]]
