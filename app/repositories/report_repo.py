from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import REPORT_FAILED, REPORT_PENDING, REPORT_SENT
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

    def find_pending_reports(self, limit: int = 100) -> Sequence[Report]:
        stmt = (
            select(Report)
            .where(Report.delivery_status == REPORT_PENDING)
            .order_by(Report.id.asc())
            .limit(limit)
        )
        return self.db.execute(stmt).scalars().all()

    def mark_as_sent(self, report_id: int, sent_at: datetime | None = None) -> Report | None:
        report = self.find_by_id(report_id)
        if report is None:
            return None

        report.delivery_status = REPORT_SENT
        report.sent_at = sent_at or datetime.now(timezone.utc)
        self.db.flush()
        return report

    def mark_as_failed(self, report_id: int) -> Report | None:
        report = self.find_by_id(report_id)
        if report is None:
            return None

        report.delivery_status = REPORT_FAILED
        self.db.flush()
        return report