# TrendRadar UI and Config Editor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a Split View Dashboard for the news feed and a DB-Driven Visual Config Editor for managing discovery sources and keywords.

**Architecture:** 
1. Database Seeding: Update `migrate_db.py` to seed `sources` and `keywords` tables from `seed_sources.yaml` if empty.
2. API Integration: Extend Next.js `web/lib/api.ts` with wrapper functions for existing `/api/sources` and `/api/keywords` endpoints.
3. Config Editor UI: Create `/web/app/settings/page.tsx` to list, add, edit, and delete sources and keywords.
4. Split View Dashboard: Redesign `/web/app/page.tsx` to include both the cluster feed (left pane) and cluster details (right pane) using client-side state for selection, avoiding full page reloads.

**Tech Stack:** Next.js (App Router), React, Tailwind CSS, Python, FastAPI, SQLAlchemy.

---

### Task 1: Seed Database with Sources and Keywords

**Files:**
- Modify: `scripts/migrate_db.py`

- [ ] **Step 1: Update database migration script to seed data**

Modify `scripts/migrate_db.py` to seed the `sources` table from `data/sources/seed_sources.yaml` if it's empty, and also seed a default keyword.

```python
import os
import sys
from pathlib import Path
import yaml

# Ensure src is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from sqlalchemy import text
from hk_aidc_news.db import engine, session_factory
from hk_aidc_news.models.base import Base
from hk_aidc_news.models.source import Source
from hk_aidc_news.models.search_keyword import SearchKeyword

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

    # Seed Data
    with session_factory() as db_session:
        # Seed Sources
        if db_session.query(Source).count() == 0:
            yaml_path = Path(__file__).parent.parent / "data" / "sources" / "seed_sources.yaml"
            if yaml_path.exists():
                payload = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
                for item in payload.get("sources", []):
                    source = Source(**item)
                    db_session.add(source)
                db_session.commit()
                print("Seeded sources from yaml.")
        
        # Seed Keywords
        if db_session.query(SearchKeyword).count() == 0:
            default_keyword = SearchKeyword(keyword="Hong Kong AI data center", active=True)
            db_session.add(default_keyword)
            db_session.commit()
            print("Seeded default search keyword.")

if __name__ == "__main__":
    migrate()
```

- [ ] **Step 2: Run migration to verify**

Run: `export PYTHONPATH=src && python scripts/migrate_db.py`
Expected: Output showing "Seeded sources from yaml" and "Seeded default search keyword".

### Task 2: Frontend API Integration for Config Editor

**Files:**
- Modify: `web/lib/types.ts`
- Modify: `web/lib/api.ts`

- [ ] **Step 1: Add types for Source and Keyword**

Add these to the end of `web/lib/types.ts`:

```typescript
export interface Source {
  id: number;
  name: string;
  base_url: string;
  rss_url?: string | null;
  region: string;
  language: string;
  source_type: string;
  discovery_mode: string;
  priority: number;
  active: boolean;
}

export interface Keyword {
  id: number;
  keyword: string;
  active: boolean;
}
```

- [ ] **Step 2: Add API wrappers**

Add these to `web/lib/api.ts`:

```typescript
import type { Source, Keyword } from "./types";

export async function getSources(): Promise<Source[]> {
  const response = await fetch(`${API_BASE_URL}/api/sources`, { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch sources");
  return response.json();
}

export async function createSource(payload: Omit<Source, "id">): Promise<Source> {
  const response = await fetch(`${API_BASE_URL}/api/sources`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("Failed to create source");
  return response.json();
}

export async function deleteSource(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/sources/${id}`, { method: "DELETE" });
  if (!response.ok) throw new Error("Failed to delete source");
}

export async function getKeywords(): Promise<Keyword[]> {
  const response = await fetch(`${API_BASE_URL}/api/keywords`, { cache: "no-store" });
  if (!response.ok) throw new Error("Failed to fetch keywords");
  return response.json();
}

export async function createKeyword(payload: Omit<Keyword, "id">): Promise<Keyword> {
  const response = await fetch(`${API_BASE_URL}/api/keywords`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("Failed to create keyword");
  return response.json();
}

export async function deleteKeyword(id: number): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/keywords/${id}`, { method: "DELETE" });
  if (!response.ok) throw new Error("Failed to delete keyword");
}
```

### Task 3: Build the Visual Config Editor UI

**Files:**
- Create: `web/app/settings/page.tsx`
- Modify: `web/app/layout.tsx`

- [ ] **Step 1: Create Settings Page Component**

Create `web/app/settings/page.tsx` as a Client Component:

```tsx
"use client";

import { useEffect, useState } from "react";
import { getSources, createSource, deleteSource, getKeywords, createKeyword, deleteKeyword } from "../../lib/api";
import type { Source, Keyword } from "../../lib/types";

export default function SettingsPage() {
  const [sources, setSources] = useState<Source[]>([]);
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  
  // Forms
  const [newSourceName, setNewSourceName] = useState("");
  const [newSourceUrl, setNewSourceUrl] = useState("");
  const [newSourceMode, setNewSourceMode] = useState("search");
  const [newKeyword, setNewKeyword] = useState("");

  const loadData = async () => {
    try {
      const [srcs, kwds] = await Promise.all([getSources(), getKeywords()]);
      setSources(srcs);
      setKeywords(kwds);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAddSource = async (e: React.FormEvent) => {
    e.preventDefault();
    await createSource({
      name: newSourceName,
      base_url: newSourceUrl,
      region: "global",
      language: "en",
      source_type: "media",
      discovery_mode: newSourceMode,
      priority: 1,
      active: true
    });
    setNewSourceName("");
    setNewSourceUrl("");
    loadData();
  };

  const handleAddKeyword = async (e: React.FormEvent) => {
    e.preventDefault();
    await createKeyword({ keyword: newKeyword, active: true });
    setNewKeyword("");
    loadData();
  };

  return (
    <main style={{ padding: "48px 24px", color: "#08131a" }}>
      <h1 style={{ fontSize: "32px", marginBottom: "24px" }}>Settings / Configuration</h1>
      
      <div style={{ display: "flex", gap: "32px" }}>
        {/* Sources Section */}
        <section style={{ flex: 2, background: "#fff", padding: "24px", borderRadius: "12px", boxShadow: "0 12px 40px rgba(0,0,0,0.08)" }}>
          <h2>Sources</h2>
          <table style={{ width: "100%", textAlign: "left", borderCollapse: "collapse", marginBottom: "24px" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid #ccc" }}>
                <th style={{ padding: "8px" }}>Name</th>
                <th style={{ padding: "8px" }}>Mode</th>
                <th style={{ padding: "8px" }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {sources.map(s => (
                <tr key={s.id} style={{ borderBottom: "1px solid #eee" }}>
                  <td style={{ padding: "8px" }}>{s.name}</td>
                  <td style={{ padding: "8px" }}>{s.discovery_mode}</td>
                  <td style={{ padding: "8px" }}>
                    <button onClick={async () => { await deleteSource(s.id); loadData(); }} style={{ color: "red", cursor: "pointer", background: "none", border: "none" }}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <form onSubmit={handleAddSource} style={{ display: "flex", gap: "8px" }}>
            <input required placeholder="Name" value={newSourceName} onChange={e => setNewSourceName(e.target.value)} style={{ padding: "8px", border: "1px solid #ccc", borderRadius: "4px" }} />
            <input required placeholder="Base URL" value={newSourceUrl} onChange={e => setNewSourceUrl(e.target.value)} style={{ padding: "8px", border: "1px solid #ccc", borderRadius: "4px" }} />
            <select value={newSourceMode} onChange={e => setNewSourceMode(e.target.value)} style={{ padding: "8px", border: "1px solid #ccc", borderRadius: "4px" }}>
              <option value="search">Search</option>
              <option value="rss">RSS</option>
            </select>
            <button type="submit" style={{ padding: "8px 16px", background: "#0f3d5d", color: "#fff", border: "none", borderRadius: "4px" }}>Add Source</button>
          </form>
        </section>

        {/* Keywords Section */}
        <section style={{ flex: 1, background: "#fff", padding: "24px", borderRadius: "12px", boxShadow: "0 12px 40px rgba(0,0,0,0.08)" }}>
          <h2>Keywords</h2>
          <ul style={{ listStyle: "none", padding: 0, marginBottom: "24px" }}>
            {keywords.map(k => (
              <li key={k.id} style={{ display: "flex", justifyContent: "space-between", padding: "8px", borderBottom: "1px solid #eee" }}>
                <span>{k.keyword}</span>
                <button onClick={async () => { await deleteKeyword(k.id); loadData(); }} style={{ color: "red", cursor: "pointer", background: "none", border: "none" }}>Delete</button>
              </li>
            ))}
          </ul>
          
          <form onSubmit={handleAddKeyword} style={{ display: "flex", gap: "8px" }}>
            <input required placeholder="New keyword" value={newKeyword} onChange={e => setNewKeyword(e.target.value)} style={{ padding: "8px", border: "1px solid #ccc", borderRadius: "4px", flex: 1 }} />
            <button type="submit" style={{ padding: "8px 16px", background: "#0f3d5d", color: "#fff", border: "none", borderRadius: "4px" }}>Add</button>
          </form>
        </section>
      </div>
    </main>
  );
}
```

- [ ] **Step 2: Add Settings to Sidebar Navigation**

Modify `web/app/layout.tsx` to add the Settings link below Pipeline Manager:

```tsx
            <Link href="/pipeline" style={{ color: "#d6e7f5", textDecoration: "none", fontSize: "16px", padding: "8px 12px", borderRadius: "8px", display: "block" }}>
              Pipeline Manager
            </Link>
            <Link href="/settings" style={{ color: "#d6e7f5", textDecoration: "none", fontSize: "16px", padding: "8px 12px", borderRadius: "8px", display: "block" }}>
              Settings
            </Link>
```

### Task 4: Refactor Dashboard into Split View

**Files:**
- Create: `web/app/SplitViewDashboard.tsx`
- Modify: `web/app/page.tsx`

- [ ] **Step 1: Create the SplitViewDashboard Client Component**

Create `web/app/SplitViewDashboard.tsx`:

```tsx
"use client";

import { useState, useEffect } from "react";
import { getClusterDetail } from "../lib/api";
import { formatClusterDate } from "../lib/format";
import AnalystActionPanel from "./clusters/[clusterId]/AnalystActionPanel";
import type { ClusterDetailResponse } from "../lib/types";

export default function SplitViewDashboard({ initialClusters }: { initialClusters: any[] }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ClusterDetailResponse | null>(null);

  useEffect(() => {
    if (selectedId) {
      getClusterDetail(selectedId).then(setDetail).catch(console.error);
    } else {
      setDetail(null);
    }
  }, [selectedId]);

  return (
    <div style={{ display: "flex", gap: "24px", height: "calc(100vh - 250px)" }}>
      {/* Left Pane: Feed */}
      <div style={{ flex: 1, overflowY: "auto", paddingRight: "12px", borderRight: "1px solid #d8e4ee" }}>
        <ul style={{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: "12px" }}>
          {initialClusters.map((cluster) => (
            <li
              key={cluster.cluster_id}
              onClick={() => setSelectedId(cluster.cluster_id)}
              style={{
                padding: "16px",
                borderRadius: "12px",
                border: selectedId === cluster.cluster_id ? "2px solid #0f3d5d" : "1px solid #d8e4ee",
                background: selectedId === cluster.cluster_id ? "#e5f0f9" : "#f8fbfd",
                cursor: "pointer",
                transition: "all 0.2s"
              }}
            >
              <div style={{ fontWeight: 600, color: "#0f3d5d", marginBottom: "8px" }}>
                {cluster.headline}
              </div>
              <div style={{ fontSize: "12px", color: "#607586" }}>
                {formatClusterDate(cluster.publish_date ?? "")} • {cluster.region}
              </div>
            </li>
          ))}
          {initialClusters.length === 0 && (
            <div style={{ padding: "20px", textAlign: "center", color: "#607586" }}>No clusters found.</div>
          )}
        </ul>
      </div>

      {/* Right Pane: Details */}
      <div style={{ flex: 2, overflowY: "auto", paddingLeft: "12px" }}>
        {!selectedId && (
          <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", color: "#8da2b3" }}>
            Select a cluster to view details
          </div>
        )}
        
        {selectedId && !detail && (
          <div style={{ display: "flex", height: "100%", alignItems: "center", justifyContent: "center", color: "#8da2b3" }}>
            Loading details...
          </div>
        )}

        {detail && (
          <div>
            <h2 style={{ fontSize: "24px", color: "#0f3d5d", marginTop: 0 }}>{detail.headline}</h2>
            
            <div style={{ background: "#f8fbfd", padding: "16px", borderRadius: "12px", border: "1px solid #d8e4ee", marginBottom: "20px" }}>
              <h3 style={{ margin: "0 0 8px", fontSize: "12px", textTransform: "uppercase", color: "#547086" }}>AI Summary</h3>
              <p style={{ margin: 0, color: "#0f3d5d", lineHeight: 1.6 }}>{detail.rationale}</p>
            </div>

            <AnalystActionPanel clusterId={detail.id.toString()} />

            <h3 style={{ fontSize: "18px", marginTop: "32px", marginBottom: "16px" }}>Sources ({detail.articles.length})</h3>
            <ul style={{ listStyle: "none", padding: 0, margin: 0, display: "grid", gap: "12px" }}>
              {detail.articles.map(article => (
                <li key={article.id} style={{ padding: "12px", border: "1px solid #d8e4ee", borderRadius: "8px" }}>
                  <a href={article.url} target="_blank" rel="noreferrer" style={{ fontSize: "14px", color: "#0f3d5d", textDecoration: "none", fontWeight: 500 }}>
                    {article.title}
                  </a>
                  <div style={{ fontSize: "12px", color: "#607586", marginTop: "4px" }}>{article.source_name}</div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Update Dashboard Server Component**

Modify `web/app/page.tsx` to replace the `<ul>` cluster list with the new `<SplitViewDashboard>` component:

```tsx
import { getClusters } from "../lib/api";
import SplitViewDashboard from "./SplitViewDashboard";

// ... keep SearchParams and type definitions ...

export default async function HomePage({ searchParams }: { searchParams: Promise<SearchParams> }) {
  const resolvedParams = await searchParams;
  const data = await getClusters(resolvedParams);

  return (
    <main style={{ minHeight: "100%", padding: "48px 24px", background: "linear-gradient(180deg, #06131d 0%, #0d2131 55%, #f3f7fb 55%, #f3f7fb 100%)", color: "#08131a" }}>
      <div style={{ maxWidth: "1200px", margin: "0 auto", display: "grid", gap: "24px" }}>
        
        {/* ... Keep the top header section exactly the same ... */}
        <section style={{ padding: "32px", borderRadius: "24px", background: "rgba(255, 255, 255, 0.08)", backdropFilter: "blur(14px)", color: "#f7fbff", boxShadow: "0 24px 80px rgba(0, 0, 0, 0.18)" }}>
          <p style={{ margin: 0, fontSize: "12px", letterSpacing: "0.24em", textTransform: "uppercase", color: "#8fd3ff" }}>Daily Cluster Feed</p>
          <h1 style={{ margin: "12px 0 8px", fontSize: "40px" }}>AI Data Center News Monitor</h1>
        </section>

        <section style={{ padding: "24px", borderRadius: "24px", background: "#ffffff", boxShadow: "0 24px 60px rgba(12, 36, 53, 0.12)" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
            <h2 style={{ margin: 0, fontSize: "24px" }}>Latest Clusters</h2>
            {/* ... Keep the existing <form> filters exactly the same ... */}
          </div>

          {/* Replace the old <ul> with the SplitViewDashboard component */}
          <SplitViewDashboard initialClusters={data.items} />
        </section>
      </div>
    </main>
  );
}
```

- [ ] **Step 3: Commit all changes**

```bash
git add scripts/ web/
git commit -m "feat: implement split view dashboard and db-driven config editor"
```