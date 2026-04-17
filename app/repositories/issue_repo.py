from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

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

    def find_open_issues(
        self,
        country: str | None = None,
        category: str | None = None,
    ) -> Sequence[Issue]:
        stmt = select(Issue).where(Issue.status == "OPEN")

        if country:
            stmt = stmt.where(Issue.country == country)
        if category:
            stmt = stmt.where(Issue.category == category)

        stmt = stmt.order_by(Issue.importance_score.desc(), Issue.last_seen_at.desc())
        return self.db.execute(stmt).scalars().all()

    def find_recent_issues(
        self,
        since: datetime,
        status: str | None = None,
        min_importance_score: float | None = None,
    ) -> Sequence[Issue]:
        stmt = select(Issue).where(Issue.last_seen_at >= since)

        if status:
            stmt = stmt.where(Issue.status == status)
        if min_importance_score is not None:
            stmt = stmt.where(Issue.importance_score >= min_importance_score)

        stmt = stmt.order_by(Issue.importance_score.desc(), Issue.last_seen_at.desc())
        return self.db.execute(stmt).scalars().all()

    def find_for_report(
        self,
        countries: list[str] | None = None,
        category_list: list[str] | None = None,
        limit: int = 20,
    ) -> Sequence[Issue]:
        stmt = select(Issue).where(Issue.status == "OPEN")

        if countries:
            stmt = stmt.where(Issue.country.in_(countries + ["GLOBAL"]))
        if category_list:
            stmt = stmt.where(Issue.category.in_(category_list))

        stmt = stmt.options(selectinload(Issue.articles))
        stmt = stmt.order_by(Issue.importance_score.desc(), Issue.article_count.desc(), Issue.last_seen_at.desc())
        stmt = stmt.limit(limit)

        return self.db.execute(stmt).scalars().all()

    def update_issue_stats(
        self,
        issue_id: int,
        article_count: int,
        last_seen_at: datetime,
        importance_score: float | None = None,
        representative_title: str | None = None,
        representative_summary: str | None = None,
    ) -> Issue | None:
        issue = self.find_by_id(issue_id)
        if issue is None:
            return None

        issue.article_count = article_count
        issue.last_seen_at = last_seen_at

        if importance_score is not None:
            issue.importance_score = importance_score
        if representative_title is not None:
            issue.representative_title = representative_title
        if representative_summary is not None:
            issue.representative_summary = representative_summary

        self.db.flush()
        return issue

    def close_issue(self, issue_id: int) -> Issue | None:
        issue = self.find_by_id(issue_id)
        if issue is None:
            return None

        issue.status = "CLOSED"
        self.db.flush()
        return issue