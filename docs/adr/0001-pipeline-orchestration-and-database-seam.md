# 1. Pipeline Orchestration and Database Seam

Date: 2026-05-21

## Status

Accepted

## Context

Currently, the pipeline services (`ingestion`, `enrichment`) are shallow modules. They accept raw dictionaries, perform network calls, and execute SQLAlchemy `db_session.add()` logic inside nested transactions. The domain logic is completely entangled with the database, destroying locality and making it impossible to test the business rules without a live database.

## Decision

We will extract the database persistence behind a `NewsRepository` Interface (a Seam).

1. **Domain Models**: We will introduce strong typing via Pydantic models (`IngestedArticle`, `EnrichedArticle`) to pass data between pipeline stages.
2. **Pure Services**: `IngestionService` and `EnrichmentService` will become deep, pure services that take domain objects in and return domain objects out, with no knowledge of SQLAlchemy.
3. **Repository Seam**: A `NewsRepository` interface will handle batch saves. When `save_ingested_articles(batch)` is called, it will persist the records and return a new list of Pydantic models with the database-generated primary keys populated.
4. **Orchestrator**: `worker.py` will act as the orchestrator, calling the services and committing to the database via the repository after each stage (Commit per stage).

## Consequences

- **Locality**: Business rules (filtering, tagging) are isolated from persistence logic.
- **Leverage**: The pipeline stages can be tested purely in memory by passing a mock `NewsRepository`.
- **Complexity**: Introduces mapping logic between Pydantic domain models and SQLAlchemy ORM models in the repository adapter.
