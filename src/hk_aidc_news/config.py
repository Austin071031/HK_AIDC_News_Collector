from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"
    database_url: str = "sqlite+pysqlite:///./app.db"
    firecrawl_api_key: str = ""
    firecrawl_base_url: str = "https://api.firecrawl.dev"
    openai_api_key: str = ""
    llm_api_key: str = ""
    llm_model: str = "gpt-4.1-mini"
    default_query_limit: int = Field(default=25, ge=1, le=100)

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("database_url must not be blank")
        return stripped_value

    @field_validator("firecrawl_api_key", "openai_api_key", "llm_api_key")
    @classmethod
    def validate_api_keys(cls, value: str) -> str:
        if value == "":
            return value

        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("API keys must not be blank")
        return stripped_value
