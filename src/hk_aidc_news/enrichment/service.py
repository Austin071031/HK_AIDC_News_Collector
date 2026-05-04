from hk_aidc_news.llm.schemas import EnrichmentResult


class EnrichmentService:
    def __init__(self, llm_client: object) -> None:
        self.llm_client = llm_client

    async def enrich(self, title: str, body: str, language: str) -> EnrichmentResult:
        try:
            return await self.llm_client.enrich(
                title=title,
                body=body,
                language=language,
            )
        except Exception:
            return EnrichmentResult(
                relevance="noise",
                confidence=0.0,
                rationale="llm_unavailable",
                tags=[],
                entities=[],
                summary="",
                semantic_key="",
            )


async def run_daily_enrichment(
    documents: list[dict[str, str]],
) -> list[dict[str, str]]:
    return documents
