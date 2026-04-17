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

    def save_all(self, articles: list[Article]) -> list[Article]:
        self.db.add_all(articles)
        self.db.flush()
        return articles

    def find_by_id(self, article_id: int) -> Article | None:
        stmt = select(Article).where(Article.id == article_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def find_by_url(self, url: str) -> Article | None:
        stmt = select(Article).where(Article.url == url)
        return self.db.execute(stmt).scalar_one_or_none()

    def find_by_dedup_key(self, dedup_key: str) -> Sequence[Article]:
        stmt = select(Article).where(Article.dedup_key == dedup_key)
        return self.db.execute(stmt).scalars().all()

    def exists_by_url(self, url: str) -> bool:
        stmt = select(Article.id).where(Article.url == url).limit(1)
        return self.db.execute(stmt).first() is not None

    def find_unlinked_articles(
        self,
        country: str | None = None,
        category: str | None = None,
        limit: int = 100,
    ) -> Sequence[Article]:
        stmt = select(Article).where(Article.issue_id.is_(None))

        if country:
            stmt = stmt.where(Article.country == country)
        if category:
            stmt = stmt.where(Article.category == category)

        stmt = stmt.order_by(Article.published_at.desc()).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def find_recent_articles(
        self,
        since: datetime,
        country: str | None = None,
        category: str | None = None,
    ) -> Sequence[Article]:
        stmt = select(Article).where(Article.published_at >= since)

        if country:
            stmt = stmt.where(Article.country == country)
        if category:
            stmt = stmt.where(Article.category == category)

        stmt = stmt.order_by(Article.published_at.desc())
        return self.db.execute(stmt).scalars().all()

    def assign_issue(self, article_id: int, issue_id: int) -> None:
        article = self.find_by_id(article_id)
        if article:
            article.issue_id = issue_id
            self.db.flush()

    def assign_issue_bulk(self, article_ids: list[int], issue_id: int) -> None:
        if not article_ids:
            return

        stmt = select(Article).where(Article.id.in_(article_ids))
        articles = self.db.execute(stmt).scalars().all()

        for article in articles:
            article.issue_id = issue_id

        self.db.flush()

    def count_by_issue_id(self, issue_id: int) -> int:
        stmt = select(Article).where(Article.issue_id == issue_id)
        return len(self.db.execute(stmt).scalars().all())
    
    def exists_by_dedup_key(self, dedup_key: str) -> bool:
        stmt = select(Article.id).where(Article.dedup_key == dedup_key).limit(1)
        return self.db.execute(stmt).first() is not None