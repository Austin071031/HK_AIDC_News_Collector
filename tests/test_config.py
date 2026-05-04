from pathlib import Path

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


def test_settings_loads_project_env_file_when_cwd_changes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_env_file = Path(__file__).resolve().parents[1] / ".env"
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("FIRECRAWL_API_KEY", raising=False)
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    project_env_file.write_text(
        "\n".join(
            [
                "APP_ENV=test",
                "DATABASE_URL=sqlite+pysqlite:///:memory:",
                "FIRECRAWL_API_KEY=firecrawl-test",
                "LLM_API_KEY=llm-test",
            ]
        ),
        encoding="utf-8",
    )

    try:
        monkeypatch.chdir(tmp_path)
        settings = Settings()
    finally:
        project_env_file.unlink(missing_ok=True)

    assert settings.app_env == "test"
    assert settings.database_url == "sqlite+pysqlite:///:memory:"
    assert settings.firecrawl_api_key == "firecrawl-test"
    assert settings.llm_api_key == "llm-test"
