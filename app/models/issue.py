from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.article import Article

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    representative_title: Mapped[str] = mapped_column(String(500), nullable=False)
    representative_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    country: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)

    importance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    article_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    last_seen_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default="OPEN")
    alert_sent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    articles: Mapped[list["Article"]] = relationship(
        "Article",
        back_populates="issue",
        passive_deletes=True,
    )
