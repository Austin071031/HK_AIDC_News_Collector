from typing import Optional
from sqlalchemy import Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hk_aidc_news.models.base import Base


class EnrichmentRecord(Base):
    __tablename__ = "enrichment_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[Optional[int]] = mapped_column(ForeignKey("articles.id"))
    relevance: Mapped[str] = mapped_column(String(32))
    confidence: Mapped[float] = mapped_column(Float)
    rationale: Mapped[str] = mapped_column(Text)
    tags: Mapped[list] = mapped_column(JSON)
    entities: Mapped[list] = mapped_column(JSON)
    summary: Mapped[str] = mapped_column(Text)
    semantic_key: Mapped[str] = mapped_column(String(255))
    model_name: Mapped[str] = mapped_column(String(255), default="")
