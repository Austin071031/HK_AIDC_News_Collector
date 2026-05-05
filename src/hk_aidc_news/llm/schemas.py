from typing import List
from pydantic import BaseModel, Field

class EnrichmentResult(BaseModel):
    relevance: str
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    tags: List[str]
    entities: List[str]
    summary: str
    semantic_key: str
