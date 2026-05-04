from sqlalchemy.orm import Session
from hk_aidc_news.llm.schemas import EnrichmentResult
from hk_aidc_news.models.enrichment import EnrichmentRecord


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
    documents: list[dict],
    db_session: Session | None = None,
) -> list[dict]:
    enriched_docs = []
    for doc in documents:
        enriched_doc = dict(doc)
        # Stub values for now
        enriched_doc["relevance"] = "high"
        enriched_doc["confidence"] = 0.9
        enriched_doc["rationale"] = "stub rationale"
        enriched_doc["tags"] = []
        enriched_doc["entities"] = []
        enriched_doc["summary"] = "stub summary"
        enriched_doc["semantic_key"] = doc.get("canonical_url", "")
        enriched_docs.append(enriched_doc)
        
        if db_session:
            record = EnrichmentRecord(
                raw_document_id=doc.get("id"),
                relevance="high",
                confidence=0.9,
                rationale="stub rationale",
                tags=[],
                entities=[],
                summary="stub summary",
                semantic_key=enriched_doc["semantic_key"],
                model_name="stub_model"
            )
            db_session.add(record)
            
    if db_session:
        db_session.flush()
        
    return enriched_docs
