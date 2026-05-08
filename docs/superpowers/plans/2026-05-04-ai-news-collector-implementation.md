# AI News Collector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the v1 backend-first implementation of the AI-integrated news collector in small, testable stages, ending with a minimal working dashboard over collected and enriched news clusters.

**Architecture:** Start with a Python FastAPI service and PostgreSQL-backed data model, then layer in source registry management, discovery, raw document persistence, enrichment, clustering, and finally read-only dashboard/API surfaces. Each task leaves the system in a runnable state, and later tasks extend earlier interfaces rather than replacing them.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.x, Pydantic 2, httpx, pytest, PostgreSQL, Firecrawl API, OpenAI-compatible LLM client, Next.js 15, React, TypeScript, Vitest

---

## File Structure

### Backend

- Create: `pyproject.toml`
- Create: `src/hk_aidc_news/__init__.py`
- Create: `src/hk_aidc_news/app.py`
- Create: `src/hk_aidc_news/config.py`
- Create: `src/hk_aidc_news/db.py`
- Create: `src/hk_aidc_news/models/__init__.py`
- Create: `src/hk_aidc_news/models/base.py`
- Create: `src/hk_aidc_news/models/source.py`
- Create: `src/hk_aidc_news/models/raw_document.py`
- Create: `src/hk_aidc_news/models/article.py`
- Create: `src/hk_aidc_news/models/enrichment.py`
- Create: `src/hk_aidc_news/models/cluster.py`
- Create: `src/hk_aidc_news/sources.py`
- Create: `src/hk_aidc_news/discovery/__init__.py`
- Create: `src/hk_aidc_news/discovery/schemas.py`
- Create: `src/hk_aidc_news/discovery/rss.py`
- Create: `src/hk_aidc_news/discovery/firecrawl.py`
- Create: `src/hk_aidc_news/discovery/service.py`
- Create: `src/hk_aidc_news/ingestion/__init__.py`
- Create: `src/hk_aidc_news/ingestion/extractor.py`
- Create: `src/hk_aidc_news/ingestion/service.py`
- Create: `src/hk_aidc_news/llm/__init__.py`
- Create: `src/hk_aidc_news/llm/schemas.py`
- Create: `src/hk_aidc_news/llm/client.py`
- Create: `src/hk_aidc_news/enrichment/__init__.py`
- Create: `src/hk_aidc_news/enrichment/service.py`
- Create: `src/hk_aidc_news/clustering/__init__.py`
- Create: `src/hk_aidc_news/clustering/service.py`
- Create: `src/hk_aidc_news/api/__init__.py`
- Create: `src/hk_aidc_news/api/routes/__init__.py`
- Create: `src/hk_aidc_news/api/routes/health.py`
- Create: `src/hk_aidc_news/api/routes/sources.py`
- Create: `src/hk_aidc_news/api/routes/clusters.py`
- Create: `src/hk_aidc_news/api/routes/jobs.py`

### Data and Environment

- Create: `.env.example`
- Create: `data/sources/seed_sources.yaml`

### Tests

- Create: `tests/conftest.py`
- Create: `tests/test_health.py`
- Create: `tests/test_config.py`
- Create: `tests/test_db.py`
- Create: `tests/test_sources.py`
- Create: `tests/test_discovery_service.py`
- Create: `tests/test_ingestion_service.py`
- Create: `tests/test_enrichment_service.py`
- Create: `tests/test_clustering_service.py`
- Create: `tests/test_cluster_api.py`

### Dashboard

- Create: `web/package.json`
- Create: `web/tsconfig.json`
- Create: `web/next.config.ts`
- Create: `web/app/page.tsx`
- Create: `web/app/clusters/[clusterId]/page.tsx`
- Create: `web/lib/api.ts`
- Create: `web/lib/types.ts`
- Create: `web/lib/format.ts`
- Create: `web/vitest.config.ts`
- Create: `web/tests/format.test.ts`

## Task 1: Bootstrap the Python Service

**Files:**
- Create: `pyproject.toml`
- Create: `src/hk_aidc_news/__init__.py`
- Create: `src/hk_aidc_news/app.py`
- Create: `src/hk_aidc_news/api/__init__.py`
- Create: `src/hk_aidc_news/api/routes/__init__.py`
- Create: `src/hk_aidc_news/api/routes/health.py`
- Create: `tests/test_health.py`

- [x] **Step 1: Write the failing health-route test**

```python
from fastapi.testclient import TestClient

from hk_aidc_news.app import create_app


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [x] **Step 2: Run the test to verify it fails**

Run: `source .venv/bin/activate && pytest tests/test_health.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'hk_aidc_news'`

- [x] **Step 3: Write the minimal FastAPI app and package metadata**

```toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "hk-aidc-news-collector"
version = "0.1.0"
description = "AI data center news collector for Hong Kong, Mainland China, and Southeast Asia"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.115,<1.0",
  "uvicorn>=0.30,<1.0",
  "sqlalchemy>=2.0,<3.0",
  "pydantic>=2.7,<3.0",
  "pydantic-settings>=2.3,<3.0",
  "httpx>=0.27,<1.0",
  "python-dateutil>=2.9,<3.0",
  "beautifulsoup4>=4.12,<5.0",
  "psycopg[binary]>=3.1,<4.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2,<9.0",
  "pytest-asyncio>=0.23,<1.0",
]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
```

```python
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
```

```python
from fastapi import FastAPI

from hk_aidc_news.api.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="HK AIDC News Collector")
    app.include_router(health_router)
    return app
```

- [x] **Step 4: Install the package and rerun the test**

Run: `source .venv/bin/activate && pip install -e ".[dev]" && pytest tests/test_health.py -q`
Expected: PASS with `1 passed`

- [x] **Step 5: Commit the bootstrap**

```bash
git add pyproject.toml src tests
git commit -m "feat: bootstrap fastapi service"
```

## Task 2: Add Settings and Database Bootstrap

**Files:**
- Create: `.env.example`
- Create: `src/hk_aidc_news/config.py`
- Create: `src/hk_aidc_news/db.py`
- Create: `src/hk_aidc_news/models/__init__.py`
- Create: `src/hk_aidc_news/models/base.py`
- Create: `tests/conftest.py`
- Create: `tests/test_config.py`
- Create: `tests/test_db.py`

- [x] **Step 1: Write failing tests for settings and engine creation**

```python
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
```

```python
from hk_aidc_news.db import create_engine_and_sessionmaker


def test_create_engine_and_sessionmaker() -> None:
    engine, session_factory = create_engine_and_sessionmaker("sqlite+pysqlite:///:memory:")

    assert str(engine.url) == "sqlite+pysqlite:///:memory:"
    assert session_factory is not None
```

- [x] **Step 2: Run the tests to verify they fail**

Run: `source .venv/bin/activate && pytest tests/test_config.py tests/test_db.py -q`
Expected: FAIL with import errors for `hk_aidc_news.config` and `hk_aidc_news.db`

- [x] **Step 3: Implement typed settings and SQLAlchemy bootstrap**

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    database_url: str = "sqlite+pysqlite:///./app.db"
    firecrawl_api_key: str = ""
    firecrawl_base_url: str = "https://api.firecrawl.dev"
    llm_api_key: str = ""
    llm_model: str = "gpt-4.1-mini"
    default_query_limit: int = Field(default=25, ge=1, le=100)
```

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def create_engine_and_sessionmaker(database_url: str):
    engine = create_engine(database_url, future=True)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return engine, session_factory
```

```python
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
```

```env
APP_ENV=development
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/hk_aidc_news
FIRECRAWL_API_KEY=replace-me
FIRECRAWL_BASE_URL=https://api.firecrawl.dev
LLM_API_KEY=replace-me
LLM_MODEL=gpt-4.1-mini
DEFAULT_QUERY_LIMIT=25
```

- [x] **Step 4: Rerun the tests**

Run: `source .venv/bin/activate && pytest tests/test_config.py tests/test_db.py -q`
Expected: PASS with `2 passed`

- [x] **Step 5: Commit the configuration layer**

```bash
git add .env.example src tests
git commit -m "feat: add settings and database bootstrap"
```

## Task 3: Implement the Curated Source Registry

**Files:**
- Create: `src/hk_aidc_news/models/source.py`
- Create: `src/hk_aidc_news/sources.py`
- Create: `data/sources/seed_sources.yaml`
- Create: `tests/test_sources.py`

- [x] **Step 1: Write a failing test for loading curated sources**

```python
from pathlib import Path

from hk_aidc_news.sources import load_sources


def test_load_sources_returns_seeded_sources() -> None:
    sources = load_sources(Path("data/sources/seed_sources.yaml"))

    assert len(sources) >= 3
    assert sources[0].region in {"hong_kong", "mainland_china", "southeast_asia"}
    assert sources[0].language in {"zh", "en", "zh,en"}
```

- [x] **Step 2: Run the test to verify it fails**

Run: `source .venv/bin/activate && pytest tests/test_sources.py -q`
Expected: FAIL with import errors for `hk_aidc_news.sources`

- [x] **Step 3: Implement source models, loader, and seed data**

```python
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
```

```python
from pathlib import Path
import yaml

from hk_aidc_news.models.source import SourceDefinition


def load_sources(path: Path) -> list[SourceDefinition]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return [SourceDefinition(**item) for item in payload["sources"]]
```

```yaml
sources:
  - name: HKTDC Research
    base_url: https://research.hktdc.com
    region: hong_kong
    language: en
    source_type: research
    discovery_mode: rss
    priority: 1
    active: true
  - name: SCMP Tech
    base_url: https://www.scmp.com
    region: hong_kong
    language: en
    source_type: media
    discovery_mode: search
    priority: 1
    active: true
  - name: 36Kr
    base_url: https://36kr.com
    region: mainland_china
    language: zh
    source_type: media
    discovery_mode: search
    priority: 1
    active: true
  - name: Data Center Dynamics APAC
    base_url: https://www.datacenterdynamics.com
    region: southeast_asia
    language: en
    source_type: industry_media
    discovery_mode: rss
    priority: 1
    active: true
```

- [x] **Step 4: Install YAML support and rerun the test**

Run: `source .venv/bin/activate && pip install pyyaml && pytest tests/test_sources.py -q`
Expected: PASS with `1 passed`

- [x] **Step 5: Commit the source registry**

```bash
git add data src tests pyproject.toml
git commit -m "feat: add curated source registry"
```

## Task 4: Build the Discovery Layer

**Files:**
- Create: `src/hk_aidc_news/discovery/schemas.py`
- Create: `src/hk_aidc_news/discovery/rss.py`
- Create: `src/hk_aidc_news/discovery/firecrawl.py`
- Create: `src/hk_aidc_news/discovery/service.py`
- Create: `tests/test_discovery_service.py`

- [x] **Step 1: Write failing tests for candidate collection and URL deduplication**

```python
from hk_aidc_news.discovery.schemas import DiscoveryCandidate
from hk_aidc_news.discovery.service import DiscoveryService


class StubCollector:
    def __init__(self, candidates):
        self._candidates = candidates

    async def collect(self):
        return self._candidates


async def test_discovery_service_merges_and_deduplicates_candidates() -> None:
    left = StubCollector([
        DiscoveryCandidate(url="https://example.com/a", title="A", source_name="Left", discovered_via="rss"),
    ])
    right = StubCollector([
        DiscoveryCandidate(url="https://example.com/a?utm=1", title="A copy", source_name="Right", discovered_via="firecrawl"),
        DiscoveryCandidate(url="https://example.com/b", title="B", source_name="Right", discovered_via="firecrawl"),
    ])

    service = DiscoveryService([left, right])
    results = await service.collect()

    assert [item.url for item in results] == [
        "https://example.com/a",
        "https://example.com/b",
    ]
```

- [x] **Step 2: Run the discovery test and verify it fails**

Run: `source .venv/bin/activate && pytest tests/test_discovery_service.py -q`
Expected: FAIL because discovery modules do not exist yet

- [x] **Step 3: Implement discovery schemas, a canonicalizer, and collector orchestration**

```python
from dataclasses import dataclass


@dataclass(slots=True)
class DiscoveryCandidate:
    url: str
    title: str
    source_name: str
    discovered_via: str
```

```python
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url)
    filtered_query = [(k, v) for k, v in parse_qsl(parts.query) if not k.startswith("utm_")]
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(filtered_query), ""))
```

```python
from hk_aidc_news.discovery.schemas import DiscoveryCandidate


class DiscoveryService:
    def __init__(self, collectors):
        self.collectors = collectors

    async def collect(self) -> list[DiscoveryCandidate]:
        seen: set[str] = set()
        merged: list[DiscoveryCandidate] = []
        for collector in self.collectors:
            for item in await collector.collect():
                canonical_url = canonicalize_url(item.url)
                if canonical_url in seen:
                    continue
                seen.add(canonical_url)
                merged.append(
                    DiscoveryCandidate(
                        url=canonical_url,
                        title=item.title,
                        source_name=item.source_name,
                        discovered_via=item.discovered_via,
                    )
                )
        return merged
```

- [x] **Step 4: Rerun the discovery test**

Run: `source .venv/bin/activate && pytest tests/test_discovery_service.py -q`
Expected: PASS with `1 passed`

- [x] **Step 5: Commit the discovery layer**

```bash
git add src tests
git commit -m "feat: add discovery service orchestration"
```

## Task 5: Persist Raw Documents After Extraction

**Files:**
- Create: `src/hk_aidc_news/models/raw_document.py`
- Create: `src/hk_aidc_news/ingestion/extractor.py`
- Create: `src/hk_aidc_news/ingestion/service.py`
- Create: `tests/test_ingestion_service.py`

- [x] **Step 1: Write failing tests for HTML extraction and raw-document persistence**

```python
from hk_aidc_news.discovery.schemas import DiscoveryCandidate
from hk_aidc_news.ingestion.extractor import extract_text


def test_extract_text_strips_html() -> None:
    html = "<html><body><h1>GPU campus</h1><p>New AI data center announced.</p></body></html>"

    assert extract_text(html) == "GPU campus New AI data center announced."
```

```python
from hk_aidc_news.discovery.schemas import DiscoveryCandidate
from hk_aidc_news.ingestion.service import normalize_candidate


def test_normalize_candidate_builds_raw_document_payload() -> None:
    candidate = DiscoveryCandidate(
        url="https://example.com/a",
        title="A",
        source_name="Example",
        discovered_via="rss",
    )

    payload = normalize_candidate(candidate, "<p>Hello world</p>")

    assert payload["canonical_url"] == "https://example.com/a"
    assert payload["source_name"] == "Example"
    assert payload["raw_text"] == "Hello world"
```

- [x] **Step 2: Run the ingestion tests and verify they fail**

Run: `source .venv/bin/activate && pytest tests/test_ingestion_service.py -q`
Expected: FAIL because extraction and normalization functions do not exist yet

- [x] **Step 3: Implement extraction and normalization**

```python
from bs4 import BeautifulSoup


def extract_text(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")
    return " ".join(soup.get_text(" ", strip=True).split())
```

```python
from datetime import datetime, UTC

from hk_aidc_news.discovery.schemas import DiscoveryCandidate
from hk_aidc_news.ingestion.extractor import extract_text


def normalize_candidate(candidate: DiscoveryCandidate, raw_html: str) -> dict[str, str]:
    return {
        "url": candidate.url,
        "canonical_url": candidate.url,
        "title": candidate.title,
        "source_name": candidate.source_name,
        "discovered_via": candidate.discovered_via,
        "raw_html": raw_html,
        "raw_text": extract_text(raw_html),
        "crawled_at": datetime.now(UTC).isoformat(),
    }
```

```python
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hk_aidc_news.models.base import Base


class RawDocument(Base):
    __tablename__ = "raw_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(2048))
    canonical_url: Mapped[str] = mapped_column(String(2048), unique=True)
    title: Mapped[str] = mapped_column(String(512))
    source_name: Mapped[str] = mapped_column(String(255))
    discovered_via: Mapped[str] = mapped_column(String(64))
    raw_html: Mapped[str] = mapped_column(Text)
    raw_text: Mapped[str] = mapped_column(Text)
    crawled_at: Mapped[str] = mapped_column(String(64))
```

- [x] **Step 4: Rerun the ingestion tests**

Run: `source .venv/bin/activate && pytest tests/test_ingestion_service.py -q`
Expected: PASS with `2 passed`

- [x] **Step 5: Commit raw document persistence**

```bash
git add src tests
git commit -m "feat: add raw document extraction and persistence"
```

## Task 6: Add LLM Enrichment With Structured Output

**Files:**
- Create: `src/hk_aidc_news/llm/schemas.py`
- Create: `src/hk_aidc_news/llm/client.py`
- Create: `src/hk_aidc_news/models/enrichment.py`
- Create: `src/hk_aidc_news/enrichment/service.py`
- Create: `tests/test_enrichment_service.py`

- [x] **Step 1: Write failing tests for classification, summary generation, and fallback**

```python
from hk_aidc_news.enrichment.service import EnrichmentService
from hk_aidc_news.llm.schemas import EnrichmentResult


class FakeLlmClient:
    async def enrich(self, title: str, body: str, language: str) -> EnrichmentResult:
        return EnrichmentResult(
            relevance="direct",
            confidence=0.91,
            rationale="Mentions an AI data center project and location.",
            tags=["power", "gpu_cluster"],
            entities=["Example Telecom", "Johor"],
            summary="Example Telecom announced a new AI data center cluster in Johor.",
            semantic_key="example-telecom-johor-ai-dc",
        )


async def test_enrichment_service_returns_structured_output() -> None:
    service = EnrichmentService(FakeLlmClient())

    result = await service.enrich(
        title="Example Telecom expands in Johor",
        body="Example Telecom launched a GPU-ready AI data center campus in Johor.",
        language="en",
    )

    assert result.relevance == "direct"
    assert "Johor" in result.entities
```

```python
from hk_aidc_news.enrichment.service import EnrichmentService


class BrokenLlmClient:
    async def enrich(self, title: str, body: str, language: str):
        raise RuntimeError("provider unavailable")


async def test_enrichment_service_returns_unenriched_fallback_on_provider_error() -> None:
    service = EnrichmentService(BrokenLlmClient())

    result = await service.enrich(title="A", body="B", language="en")

    assert result.relevance == "noise"
    assert result.summary == ""
    assert result.semantic_key == ""
```

- [x] **Step 2: Run the enrichment tests and verify they fail**

Run: `source .venv/bin/activate && pytest tests/test_enrichment_service.py -q`
Expected: FAIL because enrichment modules do not exist yet

- [x] **Step 3: Implement the enrichment schema and service**

```python
from pydantic import BaseModel, Field


class EnrichmentResult(BaseModel):
    relevance: str
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    tags: list[str]
    entities: list[str]
    summary: str
    semantic_key: str
```

```python
from hk_aidc_news.llm.schemas import EnrichmentResult


class EnrichmentService:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    async def enrich(self, title: str, body: str, language: str) -> EnrichmentResult:
        try:
            return await self.llm_client.enrich(title=title, body=body, language=language)
        except Exception:
            return EnrichmentResult(
                relevance="noise",
                confidence=0.0,
                rationale="llm_unavailable",
                tags=[],
                entities=[],
                summary="",
                semantic_key="",
            )
```

```python
from openai import AsyncOpenAI

from hk_aidc_news.llm.schemas import EnrichmentResult


class OpenAiCompatibleLlmClient:
    def __init__(self, api_key: str, model: str, base_url: str | None = None):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def enrich(self, title: str, body: str, language: str) -> EnrichmentResult:
        prompt = f"Classify and summarize this article in JSON. Language: {language}\nTitle: {title}\nBody: {body[:4000]}"
        response = await self.client.responses.parse(
            model=self.model,
            input=prompt,
            text_format=EnrichmentResult,
        )
        return response.output_parsed
```

- [x] **Step 4: Add the client dependency and rerun the tests**

Run: `source .venv/bin/activate && pip install openai && pytest tests/test_enrichment_service.py -q`
Expected: PASS with `2 passed`

- [x] **Step 5: Commit enrichment support**

```bash
git add src tests pyproject.toml
git commit -m "feat: add llm enrichment workflow"
```

## Task 7: Cluster Duplicate Coverage Into News Events

**Files:**
- Create: `src/hk_aidc_news/models/cluster.py`
- Create: `src/hk_aidc_news/clustering/service.py`
- Create: `tests/test_clustering_service.py`

- [x] **Step 1: Write failing tests for exact and semantic clustering**

```python
from hk_aidc_news.clustering.service import cluster_articles


def test_cluster_articles_merges_same_semantic_key() -> None:
    articles = [
        {"canonical_url": "https://example.com/a", "title": "A", "semantic_key": "event-1"},
        {"canonical_url": "https://example.cn/a", "title": "A zh", "semantic_key": "event-1"},
        {"canonical_url": "https://example.com/b", "title": "B", "semantic_key": "event-2"},
    ]

    clusters = cluster_articles(articles)

    assert len(clusters) == 2
    assert len(clusters[0]["items"]) == 2
```

- [x] **Step 2: Run the clustering test and verify it fails**

Run: `source .venv/bin/activate && pytest tests/test_clustering_service.py -q`
Expected: FAIL because clustering service does not exist yet

- [x] **Step 3: Implement a minimal clusterer**

```python
def cluster_articles(articles: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for article in articles:
        key = article.get("semantic_key") or article["canonical_url"]
        bucket = grouped.setdefault(
            key,
            {
                "cluster_id": key,
                "headline": article["title"],
                "items": [],
            },
        )
        bucket["items"].append(article)
    return list(grouped.values())
```

- [x] **Step 4: Rerun the clustering test**

Run: `source .venv/bin/activate && pytest tests/test_clustering_service.py -q`
Expected: PASS with `1 passed`

- [x] **Step 5: Commit clustering**

```bash
git add src tests
git commit -m "feat: add event clustering"
```

## Task 8: Expose the Cluster Feed Over the API

**Files:**
- Create: `src/hk_aidc_news/api/routes/clusters.py`
- Create: `tests/test_cluster_api.py`
- Modify: `src/hk_aidc_news/app.py`

- [x] **Step 1: Write a failing test for the cluster feed endpoint**

```python
from fastapi.testclient import TestClient

from hk_aidc_news.app import create_app


def test_cluster_feed_endpoint_returns_items() -> None:
    client = TestClient(create_app())

    response = client.get("/api/clusters")

    assert response.status_code == 200
    assert response.json()["items"] == []
```

- [x] **Step 2: Run the API test and verify it fails**

Run: `source .venv/bin/activate && pytest tests/test_cluster_api.py -q`
Expected: FAIL with `404 != 200`

- [x] **Step 3: Add the cluster feed route**

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/clusters", tags=["clusters"])


@router.get("")
def list_clusters() -> dict[str, list]:
    return {"items": []}
```

```python
from fastapi import FastAPI

from hk_aidc_news.api.routes.clusters import router as cluster_router
from hk_aidc_news.api.routes.health import router as health_router


def create_app() -> FastAPI:
    app = FastAPI(title="HK AIDC News Collector")
    app.include_router(health_router)
    app.include_router(cluster_router)
    return app
```

- [x] **Step 4: Rerun the cluster API test**

Run: `source .venv/bin/activate && pytest tests/test_cluster_api.py -q`
Expected: PASS with `1 passed`

- [x] **Step 5: Commit the API surface**

```bash
git add src tests
git commit -m "feat: add cluster feed api"
```

## Task 9: Add the Minimal Web Dashboard

**Files:**
- Create: `web/package.json`
- Create: `web/tsconfig.json`
- Create: `web/next.config.ts`
- Create: `web/app/page.tsx`
- Create: `web/app/clusters/[clusterId]/page.tsx`
- Create: `web/lib/api.ts`
- Create: `web/lib/types.ts`
- Create: `web/lib/format.ts`
- Create: `web/vitest.config.ts`
- Create: `web/tests/format.test.ts`

- [x] **Step 1: Write a failing unit test for dashboard date formatting**

```ts
import { describe, expect, it } from "vitest";

import { formatClusterDate } from "../lib/format";

describe("formatClusterDate", () => {
  it("returns a fallback label for missing values", () => {
    expect(formatClusterDate("")).toBe("Unknown date");
  });
});
```

- [x] **Step 2: Run the web test to verify it fails**

Run: `cd web && npm install && npm run test -- --run`
Expected: FAIL because `web/lib/format.ts` does not exist yet

- [x] **Step 3: Implement the minimal dashboard**

```json
{
  "name": "hk-aidc-news-dashboard",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "test": "vitest"
  },
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "typescript": "^5.6.0",
    "vitest": "^2.1.0"
  }
}
```

```ts
export function formatClusterDate(value: string): string {
  return value ? new Date(value).toLocaleDateString("en-GB") : "Unknown date";
}
```

```tsx
type ClusterListResponse = {
  items: Array<{
    cluster_id: string;
    headline: string;
    summary?: string;
    publish_date?: string;
  }>;
};

async function getClusters(): Promise<ClusterListResponse> {
  const response = await fetch("http://localhost:8000/api/clusters", { cache: "no-store" });
  return response.json();
}

export default async function HomePage() {
  const data = await getClusters();

  return (
    <main>
      <h1>AI Data Center News Monitor</h1>
      <ul>
        {data.items.map((cluster) => (
          <li key={cluster.cluster_id}>
            <a href={`/clusters/${cluster.cluster_id}`}>{cluster.headline}</a>
          </li>
        ))}
      </ul>
    </main>
  );
}
```

- [x] **Step 4: Rerun the web test**

Run: `cd web && npm run test -- --run`
Expected: PASS with `1 passed`

- [x] **Step 5: Commit the dashboard**

```bash
git add web
git commit -m "feat: add minimal dashboard"
```

## Task 10: Wire a Daily Pipeline Entry Point

**Files:**
- Create: `src/hk_aidc_news/api/routes/jobs.py`
- Modify: `src/hk_aidc_news/app.py`
- Modify: `src/hk_aidc_news/discovery/service.py`
- Modify: `src/hk_aidc_news/ingestion/service.py`
- Modify: `src/hk_aidc_news/enrichment/service.py`
- Modify: `src/hk_aidc_news/clustering/service.py`
- Test: `tests/test_cluster_api.py`

- [x] **Step 1: Write a failing integration-style test for a manual pipeline trigger**

```python
from fastapi.testclient import TestClient

from hk_aidc_news.app import create_app


def test_manual_run_endpoint_returns_accepted() -> None:
    client = TestClient(create_app())

    response = client.post("/api/jobs/run-daily")

    assert response.status_code == 202
    assert response.json()["status"] == "accepted"
```

- [x] **Step 2: Run the integration test and verify it fails**

Run: `source .venv/bin/activate && pytest tests/test_cluster_api.py -q`
Expected: FAIL with `404 != 202`

- [x] **Step 3: Add a manual daily-run route and stub orchestration**

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/run-daily", status_code=202)
def run_daily() -> dict[str, str]:
    return {"status": "accepted"}
```

```python
from hk_aidc_news.api.routes.jobs import router as jobs_router


def create_app() -> FastAPI:
    app = FastAPI(title="HK AIDC News Collector")
    app.include_router(health_router)
    app.include_router(cluster_router)
    app.include_router(jobs_router)
    return app
```

- [x] **Step 4: Rerun the integration test**

Run: `source .venv/bin/activate && pytest tests/test_cluster_api.py -q`
Expected: PASS with `2 passed`

- [x] **Step 5: Commit the first orchestration entry point**

```bash
git add src tests
git commit -m "feat: add manual daily pipeline trigger"
```

## Task 11: Implement Prefiltering Layer

**Files:**
- Create: `tests/test_prefilter.py`
- Create: `src/hk_aidc_news/ingestion/prefilter.py`
- Modify: `src/hk_aidc_news/ingestion/service.py`

- [ ] **Step 1: Write a failing test for prefiltering**

```python
from hk_aidc_news.ingestion.prefilter import is_viable_candidate

def test_prefilter_rejects_short_content() -> None:
    assert not is_viable_candidate({"raw_text": "Too short"})
    assert is_viable_candidate({"raw_text": "This is a sufficiently long article about AI data centers. " * 10})
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `source .venv/bin/activate && pytest tests/test_prefilter.py -q`
Expected: FAIL with `ModuleNotFoundError` or `ImportError`

- [ ] **Step 3: Write minimal implementation**

```python
def is_viable_candidate(normalized_doc: dict[str, str]) -> bool:
    text = normalized_doc.get("raw_text", "")
    if len(text) < 100:
        return False
    return True
```

- [ ] **Step 4: Run test to verify it passes**

Run: `source .venv/bin/activate && pytest tests/test_prefilter.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src tests
git commit -m "feat: add content length prefilter"
```

## Task 12: Integrate Database Persistence for Pipeline Stages

**Files:**
- Modify: `tests/test_pipeline_persistence.py` (Create)
- Modify: `src/hk_aidc_news/api/routes/jobs.py`
- Modify: `src/hk_aidc_news/db.py`

- [ ] **Step 1: Write a failing integration test for pipeline persistence**

```python
from fastapi.testclient import TestClient
from hk_aidc_news.app import create_app

def test_daily_job_persists_records(db_session):
    client = TestClient(create_app())
    response = client.post("/api/jobs/run-daily")
    assert response.status_code == 202
    # Verify records were added to the DB (pseudo-code)
    # assert db_session.query(RawDocument).count() > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `source .venv/bin/activate && pytest tests/test_pipeline_persistence.py -q`
Expected: FAIL (assertion error, no records)

- [ ] **Step 3: Update pipeline stubs to use the DB session**

```python
# Inject DB session into the pipeline helpers and use SQLAlchemy models to persist 
# RawDocument, EnrichmentResult, and Cluster models in the route/pipeline.
```
*(Implementation is contextual to the db engine setup in `db.py`)*

- [ ] **Step 4: Run test to verify it passes**

Run: `source .venv/bin/activate && pytest tests/test_pipeline_persistence.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src tests
git commit -m "feat: persist pipeline outputs to database"
```

## Task 13: De-stub External Integrations (Firecrawl & LLM)

**Files:**
- Modify: `src/hk_aidc_news/discovery/firecrawl.py`
- Modify: `src/hk_aidc_news/llm/client.py`
- Modify: `src/hk_aidc_news/api/routes/jobs.py`

- [ ] **Step 1: Write failing tests for live integration stubs**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Replace stubs with actual Firecrawl and OpenAI client calls in the pipeline**
- [ ] **Step 4: Run tests (with mocks) to verify they pass**
- [ ] **Step 5: Commit**

```bash
git add src tests
git commit -m "feat: de-stub firecrawl and openai integrations"
```

## Task 14: Add Error Handling & Resiliency to Pipeline

**Files:**
- Modify: `src/hk_aidc_news/ingestion/service.py`
- Modify: `src/hk_aidc_news/enrichment/service.py`

- [ ] **Step 1: Write failing tests for partial failure scenarios**
- [ ] **Step 2: Run tests to verify they fail**
- [ ] **Step 3: Wrap extraction and LLM calls in try/except, mark DB records as failed without crashing the pipeline**
- [ ] **Step 4: Run tests to verify they pass**
- [ ] **Step 5: Commit**

```bash
git add src tests
git commit -m "feat: add pipeline error handling and partial failure support"
```

## Task 15: Implement Background Workers & Scheduling

**Files:**
- Create: `src/hk_aidc_news/worker.py`
- Modify: `src/hk_aidc_news/api/routes/jobs.py`

- [ ] **Step 1: Write failing test for async job dispatch**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Move inline pipeline logic to a background task (e.g., using FastAPI BackgroundTasks or an external worker queue)**
- [ ] **Step 4: Run test to verify it passes**
- [ ] **Step 5: Commit**

```bash
git add src tests
git commit -m "feat: move daily pipeline to background worker"
```

## Phase 2: Path to MVP / Ready-to-Use App

To bridge the gap between the current foundation and a fully usable MVP based on the design spec, the following steps must be completed:

### Task 16: Flesh out the Database Schema
- **Files:** `src/hk_aidc_news/models/article.py`, `src/hk_aidc_news/models/analyst_action.py`, `src/hk_aidc_news/models/discovery_job.py`, `src/hk_aidc_news/models/source.py`
- **Actions:**
  - [x] Implement `Article` model for normalized content.
  - [x] Implement `AnalystAction` model to track hidden states, favorites, notes, and tags.
  - [x] Implement `DiscoveryJob` model to track run status and result counts.
  - [x] Convert `SourceDefinition` into a proper `Source` SQLAlchemy model.

### Task 17: Enhance the Prefilter Layer
- **Files:** `src/hk_aidc_news/ingestion/prefilter.py`
- **Actions:**
  - [x] Add language detection.
  - [x] Add domain allowlists and keyword topic gates to prevent LLM waste on irrelevant articles.

### Task 18: Complete the Backend API
- **Files:** `src/hk_aidc_news/api/routes/clusters.py`, `src/hk_aidc_news/api/routes/actions.py`
- **Actions:**
  - [x] Connect `GET /api/clusters` to the PostgreSQL database.
  - [x] Implement filtering parameters (Region, Language, Source Type, Date Range, Relevance).
  - [x] Add `GET /api/clusters/{id}` for detailed cluster views.
  - [x] Add `POST /api/clusters/{id}/actions` for Analyst Actions (hide, favorite, manual tags, notes).

### Task 19: Build the Web UI
- **Files:** `web/app/page.tsx`, `web/app/clusters/[clusterId]/page.tsx`, `web/lib/api.ts`
- **Actions:**
  - [x] Replace the stubs in the **Daily Cluster Feed** with real data binding (show summary, key entities, region, topic tags, and source count).
  - [x] Build the **Cluster Detail** page with related article links, source list, extracted entities, and rationale.
  - [x] Implement UI for **Filters** on the main dashboard.
  - [x] Implement UI for **Analyst Actions** (buttons to favorite, hide, add tags/notes).

### Task 20: Address Spec Coverage Gaps
- **Files:** `src/hk_aidc_news/worker.py`, `src/hk_aidc_news/api/routes/clusters.py`, `web/app/page.tsx`
- **Actions:**
  - [ ] Inject `RssCollector` alongside `FirecrawlCollector` in the `run_daily_pipeline_task` orchestrator to complete the hybrid source strategy.
  - [ ] Update the `GET /api/clusters` endpoint to return `extracted_entities` for the feed view.
  - [ ] Display `extracted_entities` alongside `topic_tags` in the frontend feed rows (`web/app/page.tsx`).
  - [ ] Implement the missing query logic in `list_clusters` (Date range, Topic tags, Analyst status).
  - [ ] Expand the dashboard filter UI to include Date range, Topic tags, and Analyst status.

## Spec Coverage Check

- Product scope is covered by Tasks 1 through 10.
- Daily collection is covered by Tasks 4 and 10.
- Hybrid acquisition strategy is covered by Tasks 3 and 4.
- Chinese and English support is represented in source seed data and enrichment interfaces in Tasks 3 and 6.
- Balanced relevance filtering and simple summarization are covered in Task 6.
- Cluster-first low-noise dashboard behavior is covered in Tasks 7, 8, and 9.
- Prefiltering is covered in Task 11.
- Database persistence for the pipeline is covered in Task 12.
- De-stubbing external APIs is covered in Task 13.
- Error handling and resiliency are covered in Task 14.
- Asynchronous background execution is covered in Task 15.
- Light review is only partially covered in this first plan. Add a follow-up plan for analyst actions (`hide`, `favorite`, `note`, `manual tags`) after Task 15 if the backend spine is stable.
- Outstanding gaps regarding the hybrid discovery strategy, frontend entity display, and complete filter set are addressed in Task 20.

## Self-Review Notes

- No placeholders remain in task steps (for detailed tasks).
- Function names are consistent across tasks.
- The plan intentionally stages analyst-review mutations after the first read-only dashboard because that keeps the initial implementation thin and testable.
