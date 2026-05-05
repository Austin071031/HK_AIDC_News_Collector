from typing import List, Dict, Optional
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
    documents: List[Dict],
    enrichment_service: EnrichmentService,
    model_name: str,
    db_session: Optional[Session] = None,
    relevance_threshold: float = 0.6,
    entity_threshold: float = 0.5,
) -> List[Dict]:
    enriched_docs = []
    for doc in documents:
        try:
            result = await enrichment_service.enrich(
                title=doc.get("title", ""),
                body=doc.get("body", ""),
                language=doc.get("language", "en")
            )
            
            # Thresholding logic based on spec
            if result.confidence < relevance_threshold:
                result.relevance = "noise"
                result.rationale = f"[LOW CONFIDENCE] {result.rationale}"
                result.tags = []
                
            if result.confidence < entity_threshold:
                result.entities = []
            
            enriched_doc = dict(doc)
            enriched_doc["relevance"] = result.relevance
            enriched_doc["confidence"] = result.confidence
            enriched_doc["rationale"] = result.rationale
            enriched_doc["tags"] = result.tags
            enriched_doc["entities"] = result.entities
            enriched_doc["summary"] = result.summary
            enriched_doc["semantic_key"] = result.semantic_key
            enriched_docs.append(enriched_doc)
            
            if db_session:
                record = EnrichmentRecord(
                    raw_document_id=doc.get("id"),
                    relevance=result.relevance,
                    confidence=result.confidence,
                    rationale=result.rationale,
                    tags=result.tags,
                    entities=result.entities,
                    summary=result.summary,
                    semantic_key=result.semantic_key,
                    model_name=model_name
                )
                db_session.add(record)
                db_session.flush()
        except Exception:
            if db_session:
                db_session.rollback()
            continue
            
    return enriched_docs
