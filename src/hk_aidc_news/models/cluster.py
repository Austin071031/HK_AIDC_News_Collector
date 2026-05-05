from typing import Optional
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from hk_aidc_news.models.base import Base


class Cluster(Base):
    __tablename__ = "clusters"

    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_key: Mapped[str] = mapped_column(String(255), unique=True)
    headline: Mapped[str] = mapped_column(String(512))


class ClusterItem(Base):
    __tablename__ = "cluster_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("clusters.id"))
    article_id: Mapped[Optional[int]] = mapped_column(ForeignKey("articles.id"))
    reason: Mapped[str] = mapped_column(String(255), default="")
