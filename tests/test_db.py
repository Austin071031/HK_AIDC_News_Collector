from hk_aidc_news.db import create_engine_and_sessionmaker


def test_create_engine_and_sessionmaker() -> None:
    engine, session_factory = create_engine_and_sessionmaker("sqlite+pysqlite:///:memory:")

    assert str(engine.url) == "sqlite+pysqlite:///:memory:"
    assert session_factory is not None
