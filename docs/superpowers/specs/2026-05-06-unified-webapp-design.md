# Unified Webapp and Pipeline Manager Design

## Overview
This document outlines the architecture and UI updates required to combine the existing HK AIDC News Collector pipeline and the web dashboard into a single, cohesive web application. The goal is to eliminate the need for users to run background CLI commands manually, bringing pipeline orchestration and configuration directly into the web interface.

## Architectural Changes
Currently, the pipeline (`hk_aidc_news`) is a separate Python backend/worker process, and the dashboard is a Next.js app (`web/`). 
We will introduce:
1. **Sidebar Layout**: A persistent sidebar in the Next.js app to navigate between the "News Dashboard" and "Pipeline Manager".
2. **Interactive Pipeline Execution**: A new frontend page (`/pipeline`) that triggers the FastAPI backend to run the pipeline and streams logs/progress back to the UI.
3. **Dynamic Source & Keyword Configuration**: Database-backed configuration for RSS links and Firecrawl keywords, editable via the frontend.

## Data Model Additions

### 1. Source Table Update
The existing `Source` model will be updated to support explicit RSS links.
- **New Field**: `rss_url` (String, nullable) - Allows users to specify the exact RSS feed URL, overriding the default `base_url + /rss` heuristic.

### 2. SearchKeyword Table (New)
A dedicated table to manage keywords used for Firecrawl searches.
- `id`: Primary key
- `keyword`: String (unique)
- `active`: Boolean (default True)

## UI & Workflow

### Global Layout
- A persistent left sidebar containing:
  - **Dashboard**: Links to the existing cluster feed (`/`).
  - **Pipeline Manager**: Links to the new orchestration view (`/pipeline`).

### Pipeline Manager View (`/pipeline`)
The Pipeline Manager will consist of three main sections:

#### A. Pipeline Execution & Live Logs
- **Trigger**: A prominent "Run Daily Pipeline" button.
- **Progress Stepper**: Visual indicators for pipeline stages: `Discovery -> Extraction -> Prefilter -> LLM -> Dedup`.
- **Live Terminal**: A dark-themed, scrolling text area that displays live logs streamed from the backend during execution.

#### B. RSS Sources Management
- A data table or list showing configured RSS sources.
- Actions: Add, Edit, Delete.
- Fields: Name, Base URL, RSS URL, Region, Priority, Active.

#### C. Firecrawl Keywords Management
- A list of configured Firecrawl search queries.
- Actions: Add, Delete.
- Fields: Keyword, Active status.

## Backend API Updates

### 1. Pipeline Execution
- Update `POST /api/jobs/run-daily` or create a new execution endpoint that supports live log streaming using Server-Sent Events (SSE) so the frontend can display real-time granular progress.

### 2. Source Configuration
- Add CRUD endpoints for `Source` (e.g., `GET /api/sources`, `POST /api/sources`, `PUT /api/sources/{id}`, `DELETE /api/sources/{id}`).

### 3. Keyword Configuration
- Add CRUD endpoints for `SearchKeyword` (e.g., `GET /api/keywords`, `POST /api/keywords`, `DELETE /api/keywords/{id}`).
- Update `worker.py` to fetch active `SearchKeyword` records from the database instead of using hardcoded strings.

## Error Handling & Edge Cases
- **Concurrent Pipeline Runs**: The backend must prevent or queue concurrent pipeline executions. The UI should disable the "Run" button while a job is active.
- **SSE Disconnects**: If the live log stream disconnects, the UI should attempt to reconnect or poll the job status to ensure the user knows when it completes.
- **Invalid URLs/Keywords**: The backend will validate RSS URLs and keyword lengths before saving them to the database.

## Implementation Steps (High-Level)
1. Database migrations (add `rss_url` to `Source`, create `SearchKeyword`).
2. Update `worker.py` to use dynamic keywords and explicit RSS URLs.
3. Build CRUD API endpoints for Sources and Keywords.
4. Implement SSE for pipeline log streaming.
5. Update Next.js frontend: Add Sidebar layout.
6. Build Pipeline Manager page (Execution terminal, Source management, Keyword management).
