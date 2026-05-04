# AI-Integrated News Collector Design

## Overview

This document defines the v1 design for an AI-integrated news collector focused on AI data center market intelligence across Hong Kong, Mainland China, and Southeast Asia.

The product goal is fast monitoring with daily refresh, higher-quality deduplication, and simple summarization. The primary output surface is a web dashboard used by telecom product teams for weekly market-intelligence sharing.

## Product Scope

### In Scope for v1

- Daily news collection
- Hybrid acquisition strategy
- Chinese and English source coverage
- Balanced relevance filtering
- Web dashboard as the primary interface
- Light analyst review
- LLM-based enrichment for classification, tagging, entity extraction, summarization, and semantic dedup support

### Out of Scope for v1

- Near real-time alerting
- Multi-stage editorial approval workflows
- Automated report or slide generation
- Full BI analytics platform
- Heavy source-specific scraping for every domain

## Core Requirements

### User Need

Telecom product teams need a daily, low-noise feed of AI data center market developments so they can prepare weekly internal intelligence sharing.

### Content Scope

The system monitors:

- Hong Kong
- Mainland China
- Southeast Asia

The system includes:

- Direct AI data center news
- Adjacent AI infrastructure news relevant to data center intelligence
- Telecom, power, land, cooling, interconnect, GPU cluster, cloud region, investment, and policy developments when they materially affect AI data center markets

### Quality Goals

- Faster than manual collection
- More precise than raw keyword monitoring
- Lower noise through cluster-first deduplication
- Useful bilingual coverage across Chinese and English
- Short factual summaries that reduce analyst reading time

## System Architecture

### High-Level Shape

The v1 system consists of:

- An ingestion service
- An LLM enrichment service
- A dedup and clustering service
- A relational database
- A web dashboard

### Design Principle

Deterministic systems collect and preserve source facts. The LLM interprets, normalizes, compresses, and enriches those facts.

### Source of Truth

The following fields are always stored as non-LLM facts:

- Original URL
- Canonical URL
- Source identity
- Original title
- Publication timestamp when available
- Crawl timestamp
- Raw extracted content

LLM outputs are stored as enrichment artifacts and never overwrite the raw source record.

## Data Flow

### 1. Discovery

The system runs one daily collection cycle using a hybrid source strategy:

- Curated source registry for high-value domains
- RSS and sitemap fetches where available
- Query-driven discovery through Firecrawl
- Firecrawl-based crawl fallback for pages that do not have reliable direct feed support

### 2. Extraction

Each discovered URL is fetched and normalized into a raw document record.

Direct extraction should be preferred when:

- RSS provides enough metadata
- A sitemap yields stable article URLs
- A source page is easy to parse deterministically

Firecrawl should be preferred when:

- Search-driven discovery is needed
- A source lacks structured feeds
- A page needs fallback content extraction

### 3. Prefilter

Before invoking the LLM, the system applies cheap deterministic checks:

- Domain allowlist or source priority
- Language detection
- Keyword or topic gates
- Minimum content-length threshold
- Basic article-type filtering

Only viable candidates move to the LLM enrichment stage.

### 4. LLM Enrichment

The LLM enrichment service receives normalized article input and returns structured outputs.

#### Inputs

- Title
- Body text or extracted article markdown
- Source name and domain
- Language
- Geography hints
- Discovery context such as matched query or source category

#### Responsibilities

- Relevance classification
- Topic tagging
- Entity extraction
- Bilingual normalization
- Short summarization
- Semantic similarity support for deduplication

### 5. Dedup and Clustering

The system groups related articles into event clusters using:

- Canonical URL normalization
- Content fingerprints
- Title similarity
- Publication-time proximity
- Entity overlap
- LLM semantic similarity hints

The main dashboard feed is cluster-first rather than article-first.

### 6. Storage and Presentation

Raw documents, normalized articles, enrichment results, clusters, and analyst actions are stored in the database and displayed in the web dashboard.

## LLM Workflow

### LLM Placement

The LLM works after deterministic extraction and prefiltering, not in the core crawl path.

### LLM Tasks

#### Relevance Classification

Assign one of:

- `direct`
- `adjacent`
- `noise`

Also return:

- Confidence score
- Short rationale

#### Topic Tagging

Assign controlled tags such as:

- `policy`
- `hyperscaler`
- `telecom`
- `power`
- `land`
- `cooling`
- `interconnect`
- `GPU cluster`
- `cloud region`
- `investment`
- `partnership`

#### Entity Extraction

Extract structured fields such as:

- Company names
- Operators
- Locations
- Project names
- Capacity or infrastructure signals
- Dates
- Investment indicators

#### Bilingual Normalization

Map Chinese and English terminology to a shared internal taxonomy so filters and search remain consistent.

#### Summarization

Generate a short factual analyst-facing summary of 2 to 4 sentences with no speculation.

#### Semantic Dedup Support

Produce similarity signals that help detect same-event coverage across languages and outlets.

### LLM Boundaries

The LLM is not the primary system for:

- URL discovery
- HTML extraction
- Publication-date inference
- Source identity inference

### LLM Safeguards

- Only run on prefiltered candidates
- Store model version and prompt version
- Keep structured outputs versioned
- Allow retry without re-crawling
- Preserve raw evidence for analyst review
- Mark failed items as `unenriched` instead of dropping them

## Data Model

### Source

Stores:

- Name
- Base domain
- Region
- Language
- Source type
- Priority
- Active status
- Crawl method

### DiscoveryJob

Stores:

- Job type
- Query template or source target
- Scheduled run time
- Status
- Result counts

### RawDocument

Stores:

- Fetched URL
- Canonical URL
- Title
- Raw HTML or markdown or text
- Source metadata
- Publish time
- Crawl time
- Fetch status

### Article

Stores normalized article fields:

- Clean title
- Clean body text
- Language
- Region guess
- Source reference
- Content hashes

### EnrichmentResult

Stores:

- Relevance label
- Confidence
- Rationale
- Tags
- Entities
- Summary
- Normalized taxonomy fields
- Model metadata

### Cluster

Represents the canonical event or grouped story shown in the dashboard.

### ClusterItem

Maps articles into clusters and stores merge reasons and confidence.

### AnalystAction

Stores:

- Hidden state
- Favorite state
- Notes
- Manual tags
- Review overrides

## Dashboard Workflow

### Primary View

The default dashboard view is a daily cluster feed. Each row should show:

- Representative headline
- Short summary
- Key entities
- Region
- Topic tags
- Source count
- Publish date

### Cluster Detail

Opening a cluster should show:

- All related article links
- Source list
- Raw and normalized metadata
- Extracted entities
- Cluster rationale
- Analyst notes and actions

### Filters

The dashboard should support filtering by:

- Region
- Language
- Source type
- Date range
- Relevance level
- Topic tag
- Analyst status

### Analyst Actions

Analysts can:

- Hide noise
- Favorite important items
- Add notes
- Add or remove manual tags

### Weekly Workflow

Analysts use the week view or saved filters to:

- Review the cluster feed
- Mark important clusters
- Add brief notes
- Prepare internal sharing from the reviewed set

## Dedup Strategy

### Core Rule

Deduplicate at the cluster level so one event appears once in the primary feed.

### Signal Types

#### Deterministic Signals

- Same canonical URL
- Similar normalized titles
- Similar body fingerprints
- Similar publication times
- Same source and same article path pattern where relevant

#### LLM-Assisted Signals

- Cross-lingual semantic similarity
- Same-event interpretation across different wording
- Entity and location overlap

### Merge Policy

- Auto-merge exact duplicates
- Merge near-duplicates only at high confidence
- Bias toward under-merging rather than false merges
- Keep borderline matches separate until future tuning or analyst review

## Error Handling

### Discovery Failure

- Mark run as partial failure
- Preserve successful discoveries
- Retry failed sources or queries separately

### Extraction Failure

- Store failure metadata
- Keep the discovered URL traceable
- Retry extraction without rerunning full discovery

### LLM Failure

- Store deterministic article record
- Mark enrichment as failed or `unenriched`
- Retry enrichment independently

### Dedup Failure

- Keep article visible as unclustered
- Retry clustering later

### Cost or Quota Pressure

- Reduce low-priority discovery coverage first
- Protect high-priority curated sources

## Quality Controls

### Thresholding

Use separate thresholds for:

- Relevance
- Dedup
- Entity extraction confidence

### Traceability

Store:

- Raw text
- Prompt version
- Model version
- Structured enrichment output

### Feedback Loop

Future tuning can use:

- Hidden items
- Favorited items
- Manual tag changes
- Analyst notes

## Testing and Verification

### Required Test Areas

- Source discovery
- Canonical URL normalization
- Extraction quality on Chinese and English samples
- Dedup behavior on exact, near, and cross-lingual duplicates
- Enrichment structured-output validation
- Dashboard feed and review actions

### Initial Verification Plan

- Run a dry batch on a limited source set
- Inspect false positives and false negatives
- Review cluster quality
- Review summary quality
- Confirm dashboard usability for weekly workflows

## Recommended Tech Stack

- Backend: Python with FastAPI
- Jobs and workers: Python scheduler plus async workers
- Database: PostgreSQL
- Frontend: Next.js
- Search: PostgreSQL full-text search for v1
- Discovery and crawl: Firecrawl plus direct feed fetchers

## Implementation Priorities

### Quick Wins

- Daily hybrid discovery pipeline
- Stable raw-document persistence
- Basic LLM enrichment pipeline
- Cluster-first dashboard feed
- Light analyst review actions

### Major Design Payoffs

- Structured bilingual market-intelligence dataset
- Lower analyst noise through deduplication
- Reusable enrichment pipeline for later exports, alerts, and reporting

## Risks and Mitigations

### Risk: Low-quality source extraction

Mitigation:

- Prefer direct feeds when possible
- Use Firecrawl fallback
- Store extraction failures for targeted fixes

### Risk: Over-aggressive deduplication

Mitigation:

- Bias toward under-merging
- Keep cluster confidence visible internally
- Tune using real analyst review feedback

### Risk: LLM cost or instability

Mitigation:

- Prefilter before LLM invocation
- Version prompts and models
- Retry enrichment independently
- Allow deterministic fallback records

### Risk: Taxonomy drift

Mitigation:

- Keep a controlled tag list in v1
- Add manual analyst override support

## Open Decisions Deferred Past v1

- Weekly export format
- Automated brief generation
- Real-time alerts
- Advanced source-specific adapters
- External API exposure
