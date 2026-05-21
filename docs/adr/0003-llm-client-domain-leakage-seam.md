# 3. LLM Client Domain Leakage Seam

Date: 2026-05-21

## Status

Accepted

## Context

Currently, the `OpenAiCompatibleLlmClient` contains domain-specific knowledge. Its `enrich` method hardcodes the prompt string for news extraction and explicitly references the `EnrichmentResult` Pydantic schema. This makes the LLM client a shallow module, tightly coupling infrastructure code to the news business domain, preventing reuse, and violating the separation of concerns.

## Decision

We will deepen the LLM client by defining a generic `StructuredLlmClient` interface (seam).

1. **Generic Interface**: The interface will expose generic methods like `generate_structured(system_prompt: str, user_prompt: str, schema: Type[BaseModel]) -> BaseModel` and `evaluate_boolean(system_prompt: str, text: str) -> bool`.
2. **Domain Logic Hoisting**: The domain-specific prompts (news extraction, relevance evaluation) and the `EnrichmentResult` schema will be moved up into the `EnrichmentService` and `IngestionService`.
3. **Error Handling**: The generic client will throw custom infrastructure exceptions (`LlmError`, `ParsingError`) on failure. The `EnrichmentService` will catch these and handle them according to domain rules (e.g., returning a default "noise" record).

## Consequences

- **Locality**: Prompts and schemas now live alongside the business logic in the `EnrichmentService` and `IngestionService`.
- **Leverage**: The `StructuredLlmClient` becomes a true reusable infrastructure component. It can be easily mocked for testing the enrichment logic without making real LLM calls.
- **Complexity**: Requires passing Pydantic types as arguments and handling custom exception mapping in the services.
