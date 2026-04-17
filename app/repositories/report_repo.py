from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.report import Report


class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, report: Report) -> Report:
        self.db.add(report)
        self.db.flush()
        return report

    def find_by_id(self, report_id: int) -> Report | None:
        stmt = select(Report).where(Report.id == report_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def find_by_user_id(self, user_id: int, limit: int = 20) -> Sequence[Report]:
        stmt = (
            select(Report)
            .where(Report.user_id == user_id)
            .order_by(Report.sent_at.desc())
            .limit(limit)
        )
        return self.db.execute(stmt).scalars().all()

    def find_pending_reports(self, limit: int = 100) -> Sequence[Report]:
        stmt = (
            select(Report)
            .where(Report.delivery_status == "PENDING")
            .order_by(Report.id.asc())
            .limit(limit)
        )
        return self.db.execute(stmt).scalars().all()

    def mark_as_sent(self, report_id: int, sent_at: datetime | None = None) -> Report | None:
        report = self.find_by_id(report_id)
        if report is None:
            return None

        report.delivery_status = "SENT"
        report.sent_at = sent_at or datetime.utcnow()
        self.db.flush()
        return report

    def mark_as_failed(self, report_id: int) -> Report | None:
        report = self.find_by_id(report_id)
        if report is None:
            return None

        report.delivery_status = "FAILED"
        self.db.flush()
        return report