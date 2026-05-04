import pytest
from pydantic import ValidationError

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


@pytest.mark.parametrize("app_env", ["", "staging", "production "])
def test_settings_reject_invalid_app_env(app_env: str) -> None:
    with pytest.raises(ValidationError):
        Settings(
            app_env=app_env,
            database_url="sqlite+pysqlite:///:memory:",
            firecrawl_api_key="firecrawl-test",
            llm_api_key="llm-test",
        )


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("database_url", "   "),
        ("firecrawl_api_key", " "),
        ("llm_api_key", "\t"),
    ],
)
def test_settings_reject_blank_critical_values(
    field_name: str,
    field_value: str,
) -> None:
    settings_kwargs = {
        "app_env": "test",
        "database_url": "sqlite+pysqlite:///:memory:",
        "firecrawl_api_key": "firecrawl-test",
        "llm_api_key": "llm-test",
    }
    settings_kwargs[field_name] = field_value

    with pytest.raises(ValidationError):
        Settings(**settings_kwargs)
