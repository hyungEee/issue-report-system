from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.repositories.report_repo import ReportRepository
from app.repositories.user_setting_repo import UserSettingRepository
from app.services.email_service import EmailService

logger = get_logger(__name__)


def run_send_reports(db: Session) -> dict[str, int]:
    """PENDING 상태의 리포트를 이메일로 발송합니다."""
    report_repo = ReportRepository(db)
    email_service = EmailService()

    stats = {"sent": 0, "failed": 0}

    pending_reports = list(report_repo.find_pending_reports())
    if not pending_reports:
        return stats

    users_by_id = {
        u.user_id: u
        for u in UserSettingRepository(db).find_all()
    }

    for report in pending_reports:
        user = users_by_id.get(report.user_id)
        if not user:
            logger.warning("유저 설정 없음 - report_id=%s user_id=%s", report.id, report.user_id)
            report_repo.mark_as_failed(report.id)
            stats["failed"] += 1
            continue

        subject = report.created_at.strftime("%Y년 %m월 %d일 주요 이슈 리포트")
        success = email_service.send_report(report.content, user.email, subject)
        if success:
            report_repo.mark_as_sent(report.id)
            stats["sent"] += 1
        else:
            report_repo.mark_as_failed(report.id)
            stats["failed"] += 1

    logger.info("리포트 발송 완료 - stats=%s", stats)
    return stats
