from typing import Optional
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class SystemConfig(Base):
    __tablename__ = "system_configs"

    key: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
