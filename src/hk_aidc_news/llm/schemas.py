from typing import List
from pydantic import BaseModel, Field

class EnrichmentResult(BaseModel):
    relevance: str
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    tags: List[str]
    entities: List[str]
    summary: str = Field(description="A brief paragraph summarizing the entire article.")
    key_points: List[str] = Field(description="An array of 3-5 bullet points highlighting the most critical facts, numbers, or announcements.")
    extracted_content: str = Field(description="A concise, well-structured rewrite of the article's core narrative, omitting fluff and filler, suitable for quick reading.")
    semantic_key: str
