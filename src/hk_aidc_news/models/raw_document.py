from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from hk_aidc_news.models.base import Base


class RawDocument(Base):
    __tablename__ = "raw_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String(2048))
    canonical_url: Mapped[str] = mapped_column(String(2048), unique=True)
    title: Mapped[str] = mapped_column(String(512))
    source_name: Mapped[str] = mapped_column(String(255))
    discovered_via: Mapped[str] = mapped_column(String(64))
    raw_html: Mapped[str] = mapped_column(Text)
    raw_text: Mapped[str] = mapped_column(Text)
    crawled_at: Mapped[str] = mapped_column(String(64))
