import pytest

from hk_aidc_news.enrichment.service import EnrichmentService
from hk_aidc_news.llm.schemas import EnrichmentResult


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
