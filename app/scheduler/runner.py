from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.core.logger import get_logger
from app.scheduler.jobs import collect_and_cluster_job, create_report_job, send_report_job

logger = get_logger(__name__)

_scheduler = BackgroundScheduler()


def start() -> None:
    if not settings.scheduler_enabled:
        logger.info("스케줄러 비활성화 (scheduler_enabled=False)")
        return

    interval = settings.scheduler_interval_minutes

    # 뉴스 수집 + 군집화: N분 간격으로 순차 실행
    _scheduler.add_job(collect_and_cluster_job, "interval", minutes=interval, id="collect_and_cluster")

    # 일간 리포트: 매일 report_hour:00 생성, report_hour:10 발송
    _scheduler.add_job(create_report_job, "cron", hour=settings.report_hour, minute=0, id="create_report")
    _scheduler.add_job(send_report_job, "cron", hour=settings.report_hour, minute=10, id="send_report")

    _scheduler.start()
    logger.info("스케줄러 시작 - collect/cluster interval=%dm, report cron=%02d:00/%02d:10", interval, settings.report_hour, settings.report_hour)


def stop() -> None:
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("스케줄러 종료")
