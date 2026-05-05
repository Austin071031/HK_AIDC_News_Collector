from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from hk_aidc_news.llm.schemas import EnrichmentResult
from hk_aidc_news.models.enrichment import EnrichmentRecord

# Common bilingual tags to a shared internal taxonomy
TAG_NORMALIZATION_MAP = {
    "ai": "Artificial Intelligence",
    "人工智能": "Artificial Intelligence",
    "machine learning": "Machine Learning",
    "机器学习": "Machine Learning",
    "genai": "Generative AI",
    "generative ai": "Generative AI",
    "生成式ai": "Generative AI",
    "llm": "Large Language Models",
    "large language models": "Large Language Models",
    "大语言模型": "Large Language Models",
    "大模型": "Large Language Models",
    "nlp": "Natural Language Processing",
    "自然语言处理": "Natural Language Processing",
    "computer vision": "Computer Vision",
    "计算机视觉": "Computer Vision",
    "robotics": "Robotics",
    "机器人": "Robotics",
    "cloud computing": "Cloud Computing",
    "云计算": "Cloud Computing",
    "big data": "Big Data",
    "大数据": "Big Data",
    "semiconductor": "Semiconductors",
    "semiconductors": "Semiconductors",
    "半导体": "Semiconductors",
    "chip": "Semiconductors",
    "芯片": "Semiconductors",
    "gpu": "GPUs",
    "hong kong": "Hong Kong",
    "hk": "Hong Kong",
    "香港": "Hong Kong",
    "china": "China",
    "中国": "China",
    "startup": "Startups",
    "startups": "Startups",
    "初创企业": "Startups",
    "investment": "Investment",
    "investments": "Investment",
    "投资": "Investment",
    "policy": "Policy & Regulation",
    "regulation": "Policy & Regulation",
    "政策": "Policy & Regulation",
    "监管": "Policy & Regulation",
}

def normalize_tags(tags: List[str]) -> List[str]:
    """Normalize bilingual and common tags to a shared taxonomy."""
    normalized = set()
    for tag in tags:
        clean_tag = tag.strip().lower()
        if clean_tag in TAG_NORMALIZATION_MAP:
            normalized.add(TAG_NORMALIZATION_MAP[clean_tag])
        else:
            normalized.add(tag.strip())
    return sorted(list(normalized))

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
            else:
                result.tags = normalize_tags(result.tags)
                
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
                with db_session.begin_nested():
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
            continue
            
    return enriched_docs
