# 2. Document Fetching and Cloudflare Evasion Seam

Date: 2026-05-21

## Status

Accepted

## Context

The ingestion service relies on fetching raw HTML from URLs, which is frequently blocked by Cloudflare and other protections. Currently, this logic is handled by a single `fetch_html` function in `ingestion/service.py` that hardcodes a fallback strategy (Firecrawl API -> Jina.ai -> Direct HTTP). This makes the ingestion module shallow, tightly coupling the domain logic to HTTP headers, evasion strategies, and third-party API configurations.

## Decision

We will extract the fetching logic behind a `DocumentFetcher` seam.

1. **DocumentFetcher Interface**: We will define an interface with a `fetch(url: str) -> FetchResult` method.
2. **FetchResult Object**: To improve observability and telemetry, fetchers will return a structured `FetchResult` object containing the HTML content, the name of the successful fetcher, and any errors encountered during the attempt.
3. **Chain of Responsibility**: We will implement a `ResilientFetcher` adapter that takes a list of `DocumentFetcher` instances. It will attempt to fetch the URL using each fetcher in sequence until one succeeds, providing a clean Chain of Responsibility for fallbacks.
4. **Concrete Adapters**: We will implement specific adapters for each strategy: `FirecrawlFetcher`, `JinaFetcher`, and `DirectHttpFetcher`.

## Consequences

- **Locality**: Evasion strategies and HTTP specifics are isolated in their respective adapter implementations.
- **Leverage**: The ingestion service can be tested by injecting a `MockFetcher`, completely bypassing the network. The fallback sequence can be reconfigured dynamically without changing the ingestion logic.
- **Complexity**: Increases the number of classes, replacing a single functional script with a formalized design pattern.
