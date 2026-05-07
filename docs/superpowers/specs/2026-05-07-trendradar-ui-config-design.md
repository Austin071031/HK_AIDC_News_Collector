# TrendRadar-Inspired Enhancements Design Spec

## 1. Overview
The HK AIDC News Collector is being enhanced to incorporate successful UX and product features from the `sansan0/TrendRadar` project. Specifically, this enhancement focuses on solving the "messy workflow" and "messy structure" of the current application by introducing a Split View Dashboard for easier scanning and a DB-Driven Visual Config Editor for managing discovery sources without touching YAML files.

## 2. Architecture & Components

### 2.1 Split View Dashboard
The main entry point (`/web/app/page.tsx` and related components) will be redesigned into a two-pane layout:
- **Left Pane (Timeline/Feed):** 
  - A dense, scannable list of cluster headlines, grouped by day and region.
  - Acts as a navigation menu for the clusters.
  - Visual indicators for read/unread, region, and AI relevance.
- **Right Pane (Cluster Details):**
  - Displays the full LLM-generated summary of the selected cluster.
  - Lists the source articles (links) with their individual metadata.
  - Contains the Analyst Action Panel (Favorite, Hide, Notes) which currently exists on a separate page.
  - **Interaction:** Clicking a headline in the left pane updates the right pane without a full page reload, significantly reducing friction.

### 2.2 DB-Driven Config Editor
The current configuration uses a static `seed_sources.yaml` file, which is not suitable for a product-ready web application. 
- **Database Schema Updates:** Ensure `Source` and related keyword tables in PostgreSQL are fully utilized as the source of truth for the pipeline, deprecating the static YAML file for ongoing operations.
- **API Endpoints:** 
  - `GET /api/sources` (Fetch all sources)
  - `POST /api/sources` (Create new source)
  - `PUT /api/sources/{id}` (Update source)
  - `DELETE /api/sources/{id}` (Delete source)
- **Frontend UI (`/web/app/settings/page.tsx`):**
  - A new settings dashboard with a table view of all configured sources.
  - Forms to add/edit sources, specifying `name`, `base_url`, `region`, `language`, `source_type`, and `discovery_mode` (RSS vs. Search).
  - Toggles to activate/deactivate sources dynamically.

## 3. Data Flow
1. **Config Management:** User modifies a source via the Next.js UI -> API Route (`PUT /api/sources/{id}`) -> PostgreSQL DB.
2. **Pipeline Execution:** The async worker reads active sources directly from the DB instead of the `seed_sources.yaml` file.
3. **News Consumption:** User loads the Dashboard -> Fetches clusters -> Displays in Left Pane. User clicks cluster -> Fetches details -> Displays in Right Pane. Analyst clicks "Favorite" -> API updates cluster status -> UI reflects change immediately.

## 4. Migration Plan
1. Write a one-time migration script (or use the existing `migrate_db.py` initialization) to load existing `seed_sources.yaml` entries into the database.
2. Update `worker.py` to query the DB for `active=True` sources instead of loading the YAML.
3. Build the backend API routes for CRUD operations on sources.
4. Build the Config Editor UI.
5. Refactor the Next.js Dashboard into the Split View layout.

## 5. Scope & Constraints
- We are *not* building the multi-channel push notifications or AI chat in this specific implementation phase, as prioritized by the user.
- The UI will be built using existing Next.js and Tailwind CSS configurations.