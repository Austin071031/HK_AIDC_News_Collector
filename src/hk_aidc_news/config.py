from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    database_url: str = "sqlite+pysqlite:///./app.db"
    firecrawl_api_key: str = ""
    firecrawl_base_url: str = "https://api.firecrawl.dev"
    llm_api_key: str = ""
    llm_model: str = "gpt-4.1-mini"
    default_query_limit: int = Field(default=25, ge=1, le=100)
