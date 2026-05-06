from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from hk_aidc_news.models.base import Base

class SearchKeyword(Base):
    __tablename__ = "search_keywords"

    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), unique=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
