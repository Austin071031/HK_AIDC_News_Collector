# Domain Vocabulary

## Pipeline Entities

- **DiscoveryCandidate**: A URL and basic metadata discovered by a collector, ready to be ingested.
- **IngestedArticle**: A document whose HTML has been fetched, text extracted, and passed the relevance filter. Has not yet been processed by the LLM.
- **EnrichedArticle**: An IngestedArticle that has been processed by the LLM, containing summary, tags, entities, and structured content.

## Architecture Seams

- **NewsRepository**: The interface (seam) for persisting pipeline domain objects. Handles mapping between domain objects (e.g., `IngestedArticle`) and database models (`RawDocument`, `Article`, `EnrichmentRecord`).
- **DocumentFetcher**: An interface for retrieving the raw HTML of a URL. Implementations sit behind this seam.
- **FetchResult**: A structured result returned by a `DocumentFetcher`, containing the raw HTML, the name of the fetcher that succeeded, and any errors encountered.
- **ResilientFetcher**: A composite fetcher adapter that uses the Chain of Responsibility pattern to try multiple `DocumentFetcher` implementations in sequence (e.g., Firecrawl -> Jina -> Direct).
- **StructuredLlmClient**: A generic LLM interface seam that evaluates boolean conditions and generates structured Pydantic models from split system/user prompts. It is completely unaware of the news domain and throws custom exceptions (`LlmError`, `ParsingError`) on failure.
