from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.orm import Session, selectinload

from app.core.constants import ISSUE_CLOSED, ISSUE_OPEN
from app.models.issue import Issue


class IssueRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, issue: Issue) -> Issue:
        self.db.add(issue)
        self.db.flush()
        return issue

    def find_by_id(self, issue_id: int) -> Issue | None:
        stmt = select(Issue).where(Issue.id == issue_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def find_open_with_centroid(self, category: str) -> Sequence[Issue]:
        stmt = (
            select(Issue)
            .where(
                Issue.status == ISSUE_OPEN,
                Issue.category == category,
                Issue.centroid_json.isnot(None),
            )
            .options(selectinload(Issue.articles))
        )
        return self.db.execute(stmt).scalars().all()

    def find_for_report(
        self,
        countries: list[str] | None = None,
        category_list: list[str] | None = None,
        limit: int = 20,
    ) -> Sequence[Issue]:
        stmt = select(Issue).where(Issue.status == ISSUE_OPEN)

        if countries:
            stmt = stmt.where(Issue.country.in_(countries + ["GLOBAL"]))
        if category_list:
            stmt = stmt.where(Issue.category.in_(category_list))

        stmt = stmt.order_by(Issue.importance_score.desc(), Issue.article_count.desc(), Issue.last_seen_at.desc())
        stmt = stmt.limit(limit)

        return self.db.execute(stmt).scalars().all()

    def close_stale_issues(self, cutoff: datetime) -> int:
        stmt = (
            update(Issue)
            .where(Issue.status == ISSUE_OPEN, Issue.last_seen_at < cutoff)
            .values(status=ISSUE_CLOSED)
        )
        return self.db.execute(stmt).rowcount
