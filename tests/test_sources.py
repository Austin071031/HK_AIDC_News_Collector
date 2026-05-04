from pathlib import Path

from hk_aidc_news.sources import load_sources


def test_load_sources_returns_seeded_sources() -> None:
    sources = load_sources(Path("data/sources/seed_sources.yaml"))

    assert len(sources) >= 3
    assert sources[0].region in {"hong_kong", "mainland_china", "southeast_asia"}
    assert sources[0].language in {"zh", "en", "zh,en"}
