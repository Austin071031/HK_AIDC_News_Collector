# Unified Webapp and Pipeline Manager Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Combine the pipeline execution and the news dashboard into a single web application with a sidebar, and enable UI-based configuration for sources and keywords.

**Architecture:** 
1. Database: Add `rss_url` to `Source`, create `SearchKeyword` table.
2. Backend: Add CRUD APIs for keywords and sources. Add an SSE endpoint to stream pipeline logs. Update worker to use DB records instead of hardcoded config.
3. Frontend: Add a Sidebar layout in Next.js. Create a Pipeline Manager page that manages configurations and triggers the pipeline with live logs.

**Tech Stack:** FastAPI, SQLAlchemy, Next.js, Server-Sent Events (SSE).

---

### Task 1: Database Model Updates

**Files:**
- Modify: `src/hk_aidc_news/models/source.py`
- Create: `src/hk_aidc_news/models/search_keyword.py`
- Modify: `src/hk_aidc_news/models/__init__.py`
- Create: `scripts/migrate_db.py`

- [ ] **Step 1: Add `rss_url` to `Source`**

Modify `src/hk_aidc_news/models/source.py` to add the `rss_url` column:
```python
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from hk_aidc_news.models.base import Base

class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    base_url: Mapped[str] = mapped_column(String(2048))
    rss_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    region: Mapped[str] = mapped_column(String(64))
    language: Mapped[str] = mapped_column(String(64))
    source_type: Mapped[str] = mapped_column(String(64))
    discovery_mode: Mapped[str] = mapped_column(String(64))
    priority: Mapped[int] = mapped_column(Integer, default=1)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
```

- [ ] **Step 2: Create `SearchKeyword` model**

Create `src/hk_aidc_news/models/search_keyword.py`:
```python
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from hk_aidc_news.models.base import Base

class SearchKeyword(Base):
    __tablename__ = "search_keywords"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), unique=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
```

- [ ] **Step 3: Update `__init__.py`**

Modify `src/hk_aidc_news/models/__init__.py` to import `SearchKeyword`:
```python
from .base import Base
from .article import Article
from .cluster import Cluster, ClusterItem
from .discovery_job import DiscoveryJob
from .enrichment import EnrichmentResult
from .raw_document import RawDocument
from .source import Source
from .analyst_action import AnalystAction
from .search_keyword import SearchKeyword

__all__ = [
    "Base",
    "Article",
    "Cluster",
    "ClusterItem",
    "DiscoveryJob",
    "EnrichmentResult",
    "RawDocument",
    "Source",
    "AnalystAction",
    "SearchKeyword",
]
```

- [ ] **Step 4: Create migration script**

Create `scripts/migrate_db.py`:
```python
from sqlalchemy import text
from hk_aidc_news.db import engine
from hk_aidc_news.models.base import Base

def migrate():
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE sources ADD COLUMN rss_url VARCHAR(2048);"))
            conn.commit()
            print("Added rss_url to sources.")
        except Exception as e:
            print(f"Column might already exist: {e}")
            conn.rollback()

    Base.metadata.create_all(bind=engine)
    print("Database schema updated.")

if __name__ == "__main__":
    migrate()
```

- [ ] **Step 5: Run migration**

Run: `PYTHONPATH=src python scripts/migrate_db.py`

- [ ] **Step 6: Commit**

```bash
git add src/hk_aidc_news/models scripts/migrate_db.py
git commit -m "feat: update data model for rss and keywords"
```

### Task 2: Backend API for Sources and Keywords

**Files:**
- Create: `src/hk_aidc_news/api/routes/sources.py`
- Create: `src/hk_aidc_news/api/routes/keywords.py`
- Modify: `src/hk_aidc_news/app.py`

- [ ] **Step 1: Create Keywords Router**

Create `src/hk_aidc_news/api/routes/keywords.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from hk_aidc_news.db import get_session
from hk_aidc_news.models.search_keyword import SearchKeyword

router = APIRouter(prefix="/api/keywords", tags=["keywords"])

class KeywordCreate(BaseModel):
    keyword: str
    active: bool = True

class KeywordResponse(KeywordCreate):
    id: int
    class Config:
        orm_mode = True

@router.get("", response_model=List[KeywordResponse])
def get_keywords(db: Session = Depends(get_session)):
    return db.query(SearchKeyword).all()

@router.post("", response_model=KeywordResponse)
def create_keyword(item: KeywordCreate, db: Session = Depends(get_session)):
    db_item = SearchKeyword(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{keyword_id}")
def delete_keyword(keyword_id: int, db: Session = Depends(get_session)):
    db_item = db.query(SearchKeyword).filter(SearchKeyword.id == keyword_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Keyword not found")
    db.delete(db_item)
    db.commit()
    return {"status": "deleted"}
```

- [ ] **Step 2: Create Sources Router**

Create `src/hk_aidc_news/api/routes/sources.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from hk_aidc_news.db import get_session
from hk_aidc_news.models.source import Source

router = APIRouter(prefix="/api/sources", tags=["sources"])

class SourceBase(BaseModel):
    name: str
    base_url: str
    rss_url: Optional[str] = None
    region: str
    language: str
    source_type: str
    discovery_mode: str
    priority: int = 1
    active: bool = True

class SourceResponse(SourceBase):
    id: int
    class Config:
        orm_mode = True

@router.get("", response_model=List[SourceResponse])
def get_sources(db: Session = Depends(get_session)):
    return db.query(Source).all()

@router.post("", response_model=SourceResponse)
def create_source(item: SourceBase, db: Session = Depends(get_session)):
    db_item = Source(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.put("/{source_id}", response_model=SourceResponse)
def update_source(source_id: int, item: SourceBase, db: Session = Depends(get_session)):
    db_item = db.query(Source).filter(Source.id == source_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Source not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_session)):
    db_item = db.query(Source).filter(Source.id == source_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Source not found")
    db.delete(db_item)
    db.commit()
    return {"status": "deleted"}
```

- [ ] **Step 3: Register Routers**

Modify `src/hk_aidc_news/app.py` to include new routers:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hk_aidc_news.api.routes.actions import router as actions_router
from hk_aidc_news.api.routes.clusters import router as cluster_router
from hk_aidc_news.api.routes.health import router as health_router
from hk_aidc_news.api.routes.jobs import router as jobs_router
from hk_aidc_news.api.routes.keywords import router as keywords_router
from hk_aidc_news.api.routes.sources import router as sources_router

def create_app() -> FastAPI:
    app = FastAPI(title="HK AIDC News Collector")
    
    # Add CORS middleware to allow Next.js frontend calls
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(cluster_router)
    app.include_router(actions_router)
    app.include_router(jobs_router)
    app.include_router(keywords_router)
    app.include_router(sources_router)
    return app
```

- [ ] **Step 4: Commit**

```bash
git add src/hk_aidc_news/api/routes/keywords.py src/hk_aidc_news/api/routes/sources.py src/hk_aidc_news/app.py
git commit -m "feat: add CRUD APIs for keywords and sources"
```

### Task 3: Update Worker to Use Dynamic Configuration

**Files:**
- Modify: `src/hk_aidc_news/worker.py`

- [ ] **Step 1: Fetch dynamic configs in worker**

Modify `src/hk_aidc_news/worker.py` to use `rss_url` and fetch `SearchKeyword`:
```python
import logging
import datetime
from hk_aidc_news.config import Settings
from hk_aidc_news.db import session_factory
from hk_aidc_news.clustering.service import run_daily_clustering
from hk_aidc_news.discovery.service import run_daily_discovery
from hk_aidc_news.enrichment.service import run_daily_enrichment, EnrichmentService
from hk_aidc_news.ingestion.service import run_daily_ingestion
from hk_aidc_news.discovery.firecrawl import FirecrawlCollector
from hk_aidc_news.discovery.rss import RssCollector
from hk_aidc_news.llm.client import OpenAiCompatibleLlmClient
from hk_aidc_news.models.source import Source
from hk_aidc_news.models.search_keyword import SearchKeyword

logger = logging.getLogger(__name__)

async def run_daily_pipeline_task(settings: Settings) -> None:
    logger.info("Starting daily pipeline task")
    
    with session_factory() as db_session:
        try:
            active_sources = (
                db_session.query(Source)
                .filter(Source.active == True)
                .order_by(Source.priority.asc())
                .all()
            )
            
            day_of_year = datetime.datetime.now().timetuple().tm_yday
            
            rss_feeds = {}
            for source in active_sources:
                if day_of_year % max(1, source.priority) != 0:
                    logger.info(f"Skipping source {source.name} due to priority {source.priority} on day {day_of_year}")
                    continue
                
                if source.discovery_mode == "rss":
                    if getattr(source, "rss_url", None):
                        rss_url = source.rss_url
                    else:
                        rss_url = source.base_url if source.base_url.endswith(".xml") else f"{source.base_url.rstrip('/')}/rss"
                    rss_feeds[source.name] = rss_url
            
            rss_collector = RssCollector(feeds=rss_feeds)
            
            active_keywords = db_session.query(SearchKeyword).filter(SearchKeyword.active == True).all()
            queries = [k.keyword for k in active_keywords]
            if not queries:
                queries = ["Hong Kong AI data center"]
            
            firecrawl_collector = FirecrawlCollector(
                api_key=settings.firecrawl_api_key,
                base_url=settings.firecrawl_base_url,
                queries=queries,
                limit=settings.default_query_limit,
            )
            
            llm_client = OpenAiCompatibleLlmClient(
                api_key=settings.openai_api_key,
                model=settings.llm_model,
            )
            enrichment_service = EnrichmentService(llm_client)

            logger.info("Running discovery...")
            discovered = await run_daily_discovery(collectors=[firecrawl_collector, rss_collector])
            logger.info(f"Discovered {len(discovered)} items.")
            
            logger.info("Running ingestion...")
            ingested = run_daily_ingestion(discovered, db_session)
            logger.info(f"Ingested {len(ingested)} new documents.")
            
            logger.info("Running enrichment...")
            enriched = await run_daily_enrichment(
                documents=ingested,
                enrichment_service=enrichment_service,
                model_name=settings.llm_model,
                db_session=db_session
            )
            logger.info(f"Enriched {len(enriched)} items.")
            
            logger.info("Running clustering...")
            run_daily_clustering(enriched, db_session)
            
            db_session.commit()
            logger.info("Daily pipeline task completed successfully")
        except Exception as e:
            db_session.rollback()
            logger.error(f"Error in daily pipeline task: {e}")
            raise
```

- [ ] **Step 2: Commit**

```bash
git add src/hk_aidc_news/worker.py
git commit -m "feat: use dynamic configs for rss and firecrawl"
```

### Task 4: Implement Log Streaming (SSE)

**Files:**
- Create: `src/hk_aidc_news/log_stream.py`
- Modify: `src/hk_aidc_news/api/routes/jobs.py`

- [ ] **Step 1: Create Log Queue Handler**

Create `src/hk_aidc_news/log_stream.py`:
```python
import asyncio
import logging
from typing import AsyncGenerator

# Global queue for SSE clients
log_queue = asyncio.Queue()

class QueueLogHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        try:
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(log_queue.put_nowait, msg)
        except RuntimeError:
            # If no running loop, just ignore
            pass

def setup_log_stream():
    handler = QueueLogHandler()
    handler.setFormatter(logging.Formatter('[%(asctime)s] %(message)s', datefmt="%H:%M:%S"))
    handler.setLevel(logging.INFO)
    
    # Attach to root logger or hk_aidc_news logger
    logger = logging.getLogger("hk_aidc_news")
    if not any(isinstance(h, QueueLogHandler) for h in logger.handlers):
        logger.addHandler(handler)

async def log_generator() -> AsyncGenerator[str, None]:
    while True:
        try:
            msg = await asyncio.wait_for(log_queue.get(), timeout=2.0)
            yield f"data: {msg}\n\n"
        except asyncio.TimeoutError:
            # Keep-alive
            yield f": keep-alive\n\n"
```

- [ ] **Step 2: Add SSE Endpoint**

Modify `src/hk_aidc_news/api/routes/jobs.py`:
```python
from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import StreamingResponse

from hk_aidc_news.config import Settings
from hk_aidc_news.worker import run_daily_pipeline_task
from hk_aidc_news.log_stream import setup_log_stream, log_generator

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

def get_settings() -> Settings:
    return Settings()

@router.post("/run-daily", status_code=202)
def run_daily(
    background_tasks: BackgroundTasks,
    settings: Settings = Depends(get_settings),
) -> dict:
    setup_log_stream()
    background_tasks.add_task(run_daily_pipeline_task, settings)
    return {"status": "accepted"}

@router.get("/stream")
async def stream_logs():
    setup_log_stream()
    return StreamingResponse(log_generator(), media_type="text/event-stream")
```

- [ ] **Step 3: Commit**

```bash
git add src/hk_aidc_news/log_stream.py src/hk_aidc_news/api/routes/jobs.py
git commit -m "feat: implement SSE log streaming for pipeline"
```

### Task 5: Frontend Layout & Navigation

**Files:**
- Modify: `web/app/layout.tsx`
- Modify: `web/app/page.tsx`

- [ ] **Step 1: Add Sidebar to Layout**

Modify `web/app/layout.tsx`:
```tsx
import type { ReactNode } from "react";
import Link from "next/link";

type RootLayoutProps = {
  children: ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="en">
      <body style={{ margin: 0, display: "flex", minHeight: "100vh", fontFamily: "sans-serif", background: "#f3f7fb" }}>
        {/* Sidebar */}
        <aside style={{ width: "240px", background: "#06131d", color: "#f7fbff", padding: "24px", flexShrink: 0 }}>
          <h2 style={{ fontSize: "18px", color: "#8fd3ff", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "32px" }}>HK AIDC Collector</h2>
          <nav style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <Link href="/" style={{ color: "#d6e7f5", textDecoration: "none", fontSize: "16px", padding: "8px 12px", borderRadius: "8px", display: "block" }}>
              News Feed
            </Link>
            <Link href="/pipeline" style={{ color: "#d6e7f5", textDecoration: "none", fontSize: "16px", padding: "8px 12px", borderRadius: "8px", display: "block" }}>
              Pipeline Manager
            </Link>
          </nav>
        </aside>
        
        {/* Main Content */}
        <div style={{ flexGrow: 1, overflowY: "auto" }}>
          {children}
        </div>
      </body>
    </html>
  );
}
```

- [ ] **Step 2: Update `page.tsx` styles**

Modify `web/app/page.tsx` (Change `minHeight` from `"100vh"` to `"100%"` and remove background gradient if it clashes, but keeping the gradient is fine if it looks good).
```tsx
// Just adjust the `<main>` style in web/app/page.tsx:
// Find: style={{ minHeight: "100vh", padding: "48px 24px", background: "linear-gradient..." }}
// Replace with: style={{ minHeight: "100%", padding: "48px 24px", background: "linear-gradient(180deg, #06131d 0%, #0d2131 55%, #f3f7fb 55%, #f3f7fb 100%)", color: "#08131a" }}

// ... existing code ...
import { getClusters } from "../lib/api";
import { formatClusterDate } from "../lib/format";

type SearchParams = {
  region?: string;
  relevance?: string;
  start_date?: string;
  end_date?: string;
  topic_tag?: string;
  analyst_status?: string;
};

export default async function HomePage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const resolvedParams = await searchParams;
  const data = await getClusters(resolvedParams);

  return (
    <main
      style={{
        minHeight: "100%",
        padding: "48px 24px",
        background:
          "linear-gradient(180deg, #06131d 0%, #0d2131 55%, #f3f7fb 55%, #f3f7fb 100%)",
        color: "#08131a",
      }}
    >
// ... rest of existing code ...
```

- [ ] **Step 3: Commit**

```bash
git add web/app/layout.tsx web/app/page.tsx
git commit -m "feat: add sidebar layout"
```

### Task 6: Pipeline Manager Page (Execution & Logs)

**Files:**
- Create: `web/app/pipeline/page.tsx`

- [ ] **Step 1: Create Pipeline Page Component**

Create `web/app/pipeline/page.tsx`:
```tsx
"use client";
import { useState, useEffect, useRef } from "react";

export default function PipelinePage() {
  const [logs, setLogs] = useState<string[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [logs]);

  const handleRunPipeline = async () => {
    setIsRunning(true);
    setLogs((prev) => [...prev, "> Starting Pipeline..."]);
    try {
      await fetch("http://localhost:8000/api/jobs/run-daily", { method: "POST" });
      
      const eventSource = new EventSource("http://localhost:8000/api/jobs/stream");
      eventSource.onmessage = (event) => {
        setLogs((prev) => [...prev, event.data]);
        if (event.data.includes("Daily pipeline task completed successfully") || event.data.includes("Error in daily pipeline task")) {
          setIsRunning(false);
          eventSource.close();
        }
      };
      eventSource.onerror = () => {
        setIsRunning(false);
        eventSource.close();
      };
    } catch (e) {
      setLogs((prev) => [...prev, "> Failed to trigger pipeline."]);
      setIsRunning(false);
    }
  };

  return (
    <main style={{ padding: "48px", maxWidth: "960px", margin: "0 auto" }}>
      <h1 style={{ fontSize: "32px", color: "#08131a", marginBottom: "24px" }}>Pipeline Manager</h1>
      
      <section style={{ background: "#fff", padding: "24px", borderRadius: "16px", boxShadow: "0 12px 32px rgba(0,0,0,0.05)", marginBottom: "32px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
          <h2 style={{ margin: 0, fontSize: "20px" }}>Execution Control</h2>
          <button 
            onClick={handleRunPipeline}
            disabled={isRunning}
            style={{ 
              padding: "10px 20px", 
              background: isRunning ? "#94a3b8" : "#0ea5e9", 
              color: "#fff", 
              border: "none", 
              borderRadius: "8px", 
              cursor: isRunning ? "not-allowed" : "pointer",
              fontWeight: 600
            }}
          >
            {isRunning ? "Running..." : "▶ Run Daily Pipeline"}
          </button>
        </div>
        
        <div style={{ background: "#1e293b", color: "#a1a1aa", fontFamily: "monospace", padding: "16px", borderRadius: "8px", height: "300px", overflowY: "auto", fontSize: "13px", lineHeight: "1.6" }}>
          {logs.length === 0 ? (
            <span style={{ color: "#475569" }}>Ready to run. Logs will appear here...</span>
          ) : (
            logs.map((log, i) => <div key={i}>{log}</div>)
          )}
          <div ref={logsEndRef} />
        </div>
      </section>
      
      <div style={{ color: "#64748b", fontSize: "14px", marginTop: "40px" }}>
        Note: Source and Keyword Management UI can be added below this section in future iterations, relying on the CRUD APIs created in Task 2.
      </div>
    </main>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add web/app/pipeline/page.tsx
git commit -m "feat: add pipeline manager execution ui with sse"
```
