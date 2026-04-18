from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.article import Article


class ArticleRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, article: Article) -> Article:
        self.db.add(article)
        self.db.flush()
        return article

    def get_existing_urls(self, urls: list[str]) -> set[str]:
        if not urls:
            return set()
        stmt = select(Article.url).where(Article.url.in_(urls))
        return set(self.db.execute(stmt).scalars().all())

    def get_existing_dedup_keys(self, dedup_keys: list[str]) -> set[str]:
        if not dedup_keys:
            return set()
        stmt = select(Article.dedup_key).where(Article.dedup_key.in_(dedup_keys))
        return set(self.db.execute(stmt).scalars().all())

    def find_unlinked_articles(
        self,
        category: str | None = None,
        since: datetime | None = None,
        limit: int = 100,
    ) -> Sequence[Article]:
        stmt = select(Article).where(Article.issue_id.is_(None))

        if category:
            stmt = stmt.where(Article.category == category)
        if since:
            stmt = stmt.where(Article.published_at >= since)

        stmt = stmt.order_by(Article.published_at.desc()).limit(limit)
        return self.db.execute(stmt).scalars().all()
