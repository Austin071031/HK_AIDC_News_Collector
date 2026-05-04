from hk_aidc_news.config import Settings


def test_settings_default_values() -> None:
    settings = Settings(
        app_env="test",
        database_url="sqlite+pysqlite:///:memory:",
        firecrawl_api_key="firecrawl-test",
        llm_api_key="llm-test",
    )

    assert settings.app_env == "test"
    assert settings.database_url == "sqlite+pysqlite:///:memory:"
    assert settings.default_query_limit == 25
