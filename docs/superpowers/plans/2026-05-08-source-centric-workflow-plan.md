# Source-Centric Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the application workflow from a cluster-centric view to a source-centric view, allowing users to select a news source and view its articles directly alongside LLM summaries.

**Architecture:** 
1. Backend: Implement a new API endpoint to fetch articles for a specific source, joined with their enrichment records (LLM summaries). Update the sources endpoint to optionally return article counts based on global filters.
2. Frontend: Refactor `SplitViewDashboard` to list sources in the left pane and render article cards (with summaries and links) in the right pane. Migrate `AnalystActionPanel` to target articles instead of clusters.

**Tech Stack:** FastAPI, SQLAlchemy, Next.js, React

---

### Task 1: Backend - Add Source Article Count to `GET /api/sources`

**Files:**
- Modify: `src/hk_aidc_news/api/routes/sources.py`
- Test: `tests/api/test_sources.py` (Assuming this exists or create it)

- [ ] **Step 1: Write the failing test**

```python
# tests/api/test_sources.py
from fastapi.testclient import TestClient
from hk_aidc_news.app import app

client = TestClient(app)

def test_get_sources_with_counts():
    response = client.get("/api/sources?with_counts=true")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "article_count" in data[0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/api/test_sources.py::test_get_sources_with_counts -v`
Expected: FAIL (or test file not found if it doesn't exist yet, then create it and it will fail because `article_count` is missing)

- [ ] **Step 3: Write minimal implementation**

Update `src/hk_aidc_news/api/routes/sources.py` to optionally return article counts.

```python
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, select

from hk_aidc_news.db import get_db
from hk_aidc_news.models.source import Source
from hk_aidc_news.models.article import Article

router = APIRouter()

@router.get("/", response_model=List[dict])
def get_sources(
    with_counts: bool = False,
    db: Session = Depends(get_db)
):
    if with_counts:
        stmt = (
            select(Source, func.count(Article.id).label("article_count"))
            .outerjoin(Article, Source.id == Article.source_id)
            .group_by(Source.id)
        )
        results = db.execute(stmt).all()
        
        sources = []
        for source, count in results:
            source_dict = {c.name: getattr(source, c.name) for c in source.__table__.columns}
            source_dict["article_count"] = count
            sources.append(source_dict)
        return sources
    
    # Original logic
    sources = db.query(Source).all()
    return [{c.name: getattr(source, c.name) for c in source.__table__.columns} for source in sources]
```
*(Note: Adjust the response_model and original logic to match the existing codebase in `sources.py`)*

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/api/test_sources.py::test_get_sources_with_counts -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/hk_aidc_news/api/routes/sources.py tests/api/test_sources.py
git commit -m "feat(api): add article_count to sources endpoint"
```

### Task 2: Backend - Create `GET /api/sources/{source_id}/articles`

**Files:**
- Modify: `src/hk_aidc_news/api/routes/sources.py`
- Test: `tests/api/test_source_articles.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/api/test_source_articles.py
from fastapi.testclient import TestClient
from hk_aidc_news.app import app

client = TestClient(app)

def test_get_source_articles():
    # Assuming source 1 exists
    response = client.get("/api/sources/1/articles")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "title" in data[0]
        assert "url" in data[0]
        # Should include enrichment data
        assert "enrichment" in data[0]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/api/test_source_articles.py::test_get_source_articles -v`
Expected: FAIL (404 Not Found)

- [ ] **Step 3: Write minimal implementation**

Update `src/hk_aidc_news/api/routes/sources.py` to add the new endpoint.

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from hk_aidc_news.db import get_db
from hk_aidc_news.models.source import Source
from hk_aidc_news.models.article import Article
from hk_aidc_news.models.enrichment import EnrichmentRecord
from hk_aidc_news.models.analyst_action import AnalystAction

# ... existing code ...

@router.get("/{source_id}/articles")
def get_source_articles(
    source_id: int,
    db: Session = Depends(get_db)
):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    stmt = (
        select(Article, EnrichmentRecord, AnalystAction)
        .outerjoin(EnrichmentRecord, Article.id == EnrichmentRecord.article_id)
        .outerjoin(AnalystAction, Article.id == AnalystAction.article_id)
        .where(Article.source_id == source_id)
        .order_by(Article.published_at.desc().nullslast())
    )
    
    results = db.execute(stmt).all()
    
    articles = []
    for article, enrichment, action in results:
        article_dict = {c.name: getattr(article, c.name) for c in article.__table__.columns}
        
        if enrichment:
            article_dict["enrichment"] = {
                "summary": enrichment.summary,
                "relevance": enrichment.relevance,
                "tags": enrichment.tags
            }
        else:
            article_dict["enrichment"] = None
            
        if action:
            article_dict["action"] = {
                "is_hidden": action.is_hidden,
                "is_favorite": action.is_favorite,
                "notes": action.notes,
                "tags": action.tags
            }
        else:
            article_dict["action"] = None
            
        articles.append(article_dict)
        
    return articles
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/api/test_source_articles.py::test_get_source_articles -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/hk_aidc_news/api/routes/sources.py tests/api/test_source_articles.py
git commit -m "feat(api): create endpoint for fetching a source's articles with enrichment"
```

### Task 3: Backend - Ensure Analyst Actions Support Articles

**Files:**
- Modify: `src/hk_aidc_news/api/routes/actions.py` (or wherever analyst actions are handled)

- [ ] **Step 1: Check existing implementation**
Verify if `POST /api/clusters/{cluster_id}/actions` needs to be mirrored for articles or if a generic endpoint exists. Based on the spec, we need `POST /api/articles/{article_id}/actions`.

- [ ] **Step 2: Write the failing test**

```python
# tests/api/test_article_actions.py
from fastapi.testclient import TestClient
from hk_aidc_news.app import app

client = TestClient(app)

def test_create_article_action():
    # Assuming article 1 exists
    payload = {"is_hidden": True, "is_favorite": False, "notes": "Test note", "tags": "test"}
    response = client.post("/api/articles/1/actions", json=payload)
    assert response.status_code in [200, 201]
```

- [ ] **Step 3: Write minimal implementation**

Create/Update `src/hk_aidc_news/api/routes/articles.py` (and register it in `app.py` if new).

```python
# src/hk_aidc_news/api/routes/articles.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from hk_aidc_news.db import get_db
from hk_aidc_news.models.article import Article
from hk_aidc_news.models.analyst_action import AnalystAction

router = APIRouter()

class ActionPayload(BaseModel):
    is_hidden: bool = False
    is_favorite: bool = False
    notes: Optional[str] = None
    tags: Optional[str] = None

@router.post("/{article_id}/actions")
def submit_article_action(
    article_id: int,
    payload: ActionPayload,
    db: Session = Depends(get_db)
):
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    action = db.query(AnalystAction).filter(AnalystAction.article_id == article_id).first()
    
    if action:
        action.is_hidden = payload.is_hidden
        action.is_favorite = payload.is_favorite
        action.notes = payload.notes
        action.tags = payload.tags
    else:
        action = AnalystAction(
            article_id=article_id,
            is_hidden=payload.is_hidden,
            is_favorite=payload.is_favorite,
            notes=payload.notes,
            tags=payload.tags
        )
        db.add(action)
        
    db.commit()
    db.refresh(action)
    return action
```
*Note: Make sure to register this router in `src/hk_aidc_news/app.py` if `articles.py` is new.*

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/api/test_article_actions.py::test_create_article_action -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/hk_aidc_news/api/routes/articles.py tests/api/test_article_actions.py src/hk_aidc_news/app.py
git commit -m "feat(api): add endpoint for article analyst actions"
```

### Task 4: Frontend - Update API Client Functions

**Files:**
- Modify: `web/lib/api.ts`
- Modify: `web/lib/types.ts`

- [ ] **Step 1: Update Types**

```typescript
// web/lib/types.ts (additions)

export interface ArticleEnrichment {
  summary: string;
  relevance: string;
  tags: string[];
}

export interface ArticleAction {
  is_hidden: boolean;
  is_favorite: boolean;
  notes: string | null;
  tags: string | null;
}

export interface SourceArticle {
  id: number;
  title: string;
  url: string;
  published_at: string | null;
  enrichment: ArticleEnrichment | null;
  action: ArticleAction | null;
}

export interface SourceWithCount extends Source {
  article_count?: number;
}
```

- [ ] **Step 2: Add API Functions**

```typescript
// web/lib/api.ts (additions/modifications)

// Update getSources to accept searchParams
export async function getSources(
  searchParams?: { [key: string]: string | string[] | undefined }
): Promise<SourceWithCount[]> {
  const url = new URL(`${API_BASE_URL}/api/sources`);
  url.searchParams.append("with_counts", "true");
  
  if (searchParams) {
    Object.entries(searchParams).forEach(([key, value]) => {
      if (value) {
        url.searchParams.append(key, String(value));
      }
    });
  }
  
  const response = await fetch(url.toString(), { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch sources");
  return response.json();
}

export async function getSourceArticles(sourceId: string): Promise<SourceArticle[]> {
  const response = await fetch(`${API_BASE_URL}/api/sources/${sourceId}/articles`, {
    cache: "no-store",
  });
  if (!response.ok) throw new Error("Failed to fetch source articles");
  return response.json();
}

export async function submitArticleAction(articleId: string, payload: ActionPayload) {
  const response = await fetch(`${API_BASE_URL}/api/articles/${articleId}/actions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("Failed to submit action");
  return response.json();
}
```

- [ ] **Step 3: Commit**

```bash
git add web/lib/api.ts web/lib/types.ts
git commit -m "feat(web): add api client functions for sources and articles"
```

### Task 5: Frontend - Refactor `SplitViewDashboard.tsx`

**Files:**
- Modify: `web/app/SplitViewDashboard.tsx`
- Rename/Modify: `web/app/clusters/[clusterId]/AnalystActionPanel.tsx` -> `web/app/components/AnalystActionPanel.tsx` (or similar)

- [ ] **Step 1: Move and update AnalystActionPanel**
Move `AnalystActionPanel.tsx` to a shared components folder (e.g., `web/components/AnalystActionPanel.tsx`). Update it to accept `articleId` instead of `clusterId` and call `submitArticleAction`.

- [ ] **Step 2: Refactor SplitViewDashboard**

```tsx
// web/app/SplitViewDashboard.tsx
"use client";

import { useState, useEffect } from "react";
import { getSourceArticles } from "../lib/api";
import AnalystActionPanel from "../components/AnalystActionPanel"; // Adjust path
import type { SourceWithCount, SourceArticle } from "../lib/types";

export default function SplitViewDashboard({ initialSources }: { initialSources: SourceWithCount[] }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [articles, setArticles] = useState<SourceArticle[] | null>(null);

  useEffect(() => {
    if (selectedId) {
      setArticles(null); // Reset while loading
      getSourceArticles(selectedId).then(setArticles).catch(console.error);
    } else {
      setArticles(null);
    }
  }, [selectedId]);

  return (
    <div style={{ display: "flex", gap: "24px", height: "calc(100vh - 250px)" }}>
      {/* Left Pane: Sources List */}
      <div style={{ flex: 1, overflowY: "auto", paddingRight: "12px", borderRight: "1px solid #d8e4ee" }}>
        <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: "12px" }}>
          {initialSources.map((source) => (
            <li
              key={source.id}
              onClick={() => setSelectedId(source.id.toString())}
              style={{
                padding: "16px",
                borderRadius: "12px",
                border: selectedId === source.id.toString() ? "2px solid #0f3d5d" : "1px solid #d8e4ee",
                background: selectedId === source.id.toString() ? "#e5f0f9" : "#f8fbfd",
                cursor: "pointer",
                transition: "all 0.2s"
              }}
            >
              <div style={{ fontWeight: 600, color: "#0f3d5d", marginBottom: "4px" }}>
                {source.name}
              </div>
              <div style={{ fontSize: "12px", color: "#607586" }}>
                {source.region} • {source.article_count || 0} articles
              </div>
            </li>
          ))}
          {initialSources.length === 0 && (
            <div style={{ padding: "20px", textAlign: "center", color: "#607586" }}>No sources found.</div>
          )}
        </ul>
      </div>

      {/* Right Pane: Article Cards */}
      <div style={{ flex: 2, overflowY: "auto", paddingLeft: "12px" }}>
        {!selectedId && (
          <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", color: "#8da2b3" }}>
            Select a source to view articles
          </div>
        )}
        
        {selectedId && !articles && (
          <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", color: "#8da2b3" }}>
            Loading articles...
          </div>
        )}

        {articles && (
          <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            {articles.length === 0 ? (
               <div style={{ textAlign: "center", color: "#8da2b3", marginTop: "40px" }}>No articles found for this source.</div>
            ) : (
               articles.map(article => (
                 <div key={article.id} style={{ border: "1px solid #d8e4ee", borderRadius: "12px", padding: "20px", background: "#fff" }}>
                   <h3 style={{ margin: "0 0 12px 0", fontSize: "20px", color: "#0f3d5d" }}>
                     <a href={article.url} target="_blank" rel="noreferrer" style={{ textDecoration: "none", color: "inherit" }}>
                       {article.title}
                     </a>
                   </h3>
                   
                   <div style={{ background: "#f8fbfd", padding: "12px", borderRadius: "8px", border: "1px solid #e1ebf2", marginBottom: "16px" }}>
                     <h4 style={{ margin: "0 0 4px 0", fontSize: "11px", textTransform: "uppercase", color: "#547086" }}>AI Summary</h4>
                     <p style={{ margin: 0, color: "#2d4456", fontSize: "14px", lineHeight: 1.5 }}>
                       {article.enrichment?.summary || "Summary pending..."}
                     </p>
                   </div>

                   <AnalystActionPanel articleId={article.id.toString()} initialAction={article.action} />
                 </div>
               ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add web/app/SplitViewDashboard.tsx web/components/AnalystActionPanel.tsx
git commit -m "feat(web): redesign split view for source-centric workflow"
```

### Task 6: Frontend - Update `page.tsx`

**Files:**
- Modify: `web/app/page.tsx`

- [ ] **Step 1: Modify data fetching in page.tsx**

```tsx
// web/app/page.tsx
// Replace getClusters with getSources
import { getSources } from "../lib/api";
import SplitViewDashboard from "./SplitViewDashboard";

// ... existing code ...

export default async function HomePage({
  searchParams,
}: {
  searchParams: Promise<SearchParams>;
}) {
  const resolvedParams = await searchParams;
  // Fetch sources instead of clusters
  const sources = await getSources(resolvedParams);

  return (
    <main
      style={{
        // ... existing styles ...
      }}
    >
      <div
        style={{
          // ... existing styles ...
        }}
      >
        <section
          style={{
            // ... existing styles ...
          }}
        >
          {/* ... existing header content ... */}
        </section>

        <section
          style={{
            // ... existing styles ...
          }}
        >
          <div
            style={{
              // ... existing styles ...
            }}
          >
            <h2 style={{ margin: 0, fontSize: "24px" }}>News Sources</h2>
            {/* ... existing form filters ... */}
          </div>

          <SplitViewDashboard initialSources={sources} />
        </section>
      </div>
    </main>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add web/app/page.tsx
git commit -m "feat(web): wire up sources to main dashboard page"
```
