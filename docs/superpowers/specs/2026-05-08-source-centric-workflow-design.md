# Source-Centric Workflow Redesign Spec

## 1. Overview
The current UI displays a "Cluster-centric" feed where news articles are grouped into clusters. Clicking a cluster shows the cluster details and a list of source links.
The new workflow will be "Source-centric". The left panel will display a list of news sources. Clicking a source will populate the right panel with a list of article cards from that source. Each card will contain the article title, an LLM-generated summary, and a direct link to the full content.

## 2. Architecture & Data Flow

### Backend API Changes
1.  **New Endpoint**: `GET /api/sources/{source_id}/articles`
    *   Fetches articles for a specific source.
    *   Joins `Article` with `EnrichmentRecord` to include the LLM `summary`, `relevance`, and `tags`.
    *   Supports global filters (`region`, `relevance`, `start_date`, `end_date`, `topic_tag`, `analyst_status`).
2.  **Update Sources Endpoint**: `GET /api/sources`
    *   Update to optionally return an `article_count` based on active global filters to prevent users from clicking sources with zero matching articles.
3.  **Analyst Actions**: 
    *   The `AnalystAction` model already supports `article_id`.
    *   Ensure routes support creating/updating actions via `/api/articles/{article_id}/actions`.

### Frontend Changes
1.  **Page Layout (`web/app/page.tsx`)**:
    *   Update `getClusters` to `getSources` (or a new specialized fetcher that gets sources with counts).
    *   Keep the existing global filters but apply them to the source/article fetching logic.
2.  **Dashboard Component (`web/app/SplitViewDashboard.tsx`)**:
    *   **Left Pane**: Render a list of `Source` items instead of `Cluster` items. Show source name, region, and matching article count.
    *   **Right Pane**: When a source is selected, fetch and render a list of Article Cards.
    *   **Article Card Component**: 
        *   Display `article.title`.
        *   Display `enrichment.summary` (LLM Summary).
        *   Include a `<a target="_blank">` link pointing to `article.url`.
        *   Embed the `AnalystActionPanel` within or alongside the card, targeting `article_id` instead of `cluster_id`.

## 3. Data Models
No schema migrations are strictly required for the core feature, as `Article`, `Source`, `EnrichmentRecord`, and `AnalystAction` already exist and have the necessary foreign keys.
*   `Article` has `source_id`.
*   `EnrichmentRecord` has `article_id` and `summary`.
*   `AnalystAction` has `article_id`.

## 4. Error Handling & Edge Cases
*   **Empty States**: If a source has no articles matching the filters, display a clear "No articles found for this source" message in the right panel.
*   **Missing Enrichment**: If an article has not yet been processed by the LLM (no `EnrichmentRecord`), display a fallback text (e.g., "Summary pending...").
*   **Loading States**: Implement skeleton loaders in the right panel while fetching a source's articles.

## 5. Implementation Phasing
1.  **Phase 1 (Backend)**: Implement `GET /api/sources/{source_id}/articles` and ensure it returns joined enrichment data.
2.  **Phase 2 (Frontend)**: Update `SplitViewDashboard.tsx` to use the new layout and component structure.
3.  **Phase 3 (Refinement)**: Add article counts to the left panel sources list.
4.  **Phase 4 (Cleanup - Future)**: Deprecate and remove cluster-related code, pipelines, and models once the source-centric workflow is fully validated.
