import pytest

from hk_aidc_news.enrichment.service import EnrichmentService, normalize_tags
from hk_aidc_news.llm.schemas import EnrichmentResult

def test_normalize_tags() -> None:
    tags = ["AI", "人工智能", "Machine Learning", "gpu", "Unknown Tag"]
    normalized = normalize_tags(tags)
    
    assert "Artificial Intelligence" in normalized
    assert "Machine Learning" in normalized
    assert "GPUs" in normalized
    assert "Unknown Tag" in normalized
    # "AI" and "人工智能" should be merged into "Artificial Intelligence"
    assert "AI" not in normalized
    assert "人工智能" not in normalized
    assert "gpu" not in normalized
    assert len(normalized) == 4

class FakeLlmClient:
    async def enrich(self, title: str, body: str, language: str) -> EnrichmentResult:
        return EnrichmentResult(
            relevance="direct",
            confidence=0.91,
            rationale="Mentions an AI data center project and location.",
            tags=["power", "gpu_cluster"],
            entities=["Example Telecom", "Johor"],
            summary="Example Telecom announced a new AI data center cluster in Johor.",
            semantic_key="example-telecom-johor-ai-dc",
        )


@pytest.mark.asyncio
async def test_enrichment_service_returns_structured_output() -> None:
    service = EnrichmentService(FakeLlmClient())

    result = await service.enrich(
        title="Example Telecom expands in Johor",
        body="Example Telecom launched a GPU-ready AI data center campus in Johor.",
        language="en",
    )

    assert result.relevance == "direct"
    assert "Johor" in result.entities


class BrokenLlmClient:
    async def enrich(self, title: str, body: str, language: str) -> EnrichmentResult:
        raise RuntimeError("provider unavailable")


@pytest.mark.asyncio
async def test_enrichment_service_returns_unenriched_fallback_on_provider_error() -> (
    None
):
    service = EnrichmentService(BrokenLlmClient())

    result = await service.enrich(title="A", body="B", language="en")

    assert result.relevance == "noise"
    assert result.summary == ""
    assert result.semantic_key == ""


@pytest.mark.asyncio
async def test_run_daily_enrichment_partial_failure() -> None:
    from hk_aidc_news.enrichment.service import run_daily_enrichment

    class FlakyLlmClient:
        async def enrich(self, title: str, body: str, language: str) -> EnrichmentResult:
            if title == "Fail":
                raise RuntimeError("LLM exploded")
            return EnrichmentResult(
                relevance="direct",
                confidence=0.9,
                rationale="Pass",
                tags=[],
                entities=[],
                summary="Pass",
                semantic_key="pass"
            )

    # In our implementation, EnrichmentService.enrich catches exceptions and returns a fallback.
    # But let's test if the loop in run_daily_enrichment handles exceptions that might leak
    # or if we wrap the whole call in the loop. The instruction says: 
    # "Wrap LLM calls in try/except. If extraction or LLM enrichment fails for a single document... continue processing the rest."
    # To truly test run_daily_enrichment, we can make EnrichmentService.enrich itself raise an exception,
    # or mock it to raise an exception.
    class FlakyEnrichmentService:
        async def enrich(self, title: str, body: str, language: str) -> EnrichmentResult:
            if title == "Fail":
                raise ValueError("Enrichment failed")
            return EnrichmentResult(
                relevance="direct",
                confidence=0.9,
                rationale="Pass",
                tags=[],
                entities=[],
                summary="Pass",
                semantic_key="pass"
            )

    docs = [
        {"id": 1, "title": "Fail", "body": "B", "language": "en"},
        {"id": 2, "title": "Pass", "body": "B", "language": "en"}
    ]

    service = FlakyEnrichmentService()
    results = await run_daily_enrichment(docs, service, "test_model")
    
    # Depending on implementation, it might return 1 document or 2 (with 1 failed).
    # If it "ensure it doesn't crash the pipeline but continue processing the rest",
    # it should at least return the one that passed.
    assert len(results) >= 1
    assert any(r["title"] == "Pass" for r in results)

