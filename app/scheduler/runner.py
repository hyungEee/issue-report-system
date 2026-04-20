from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.core.constants import (
    REPORT_CREATE_MINUTE,
    REPORT_HOUR,
    REPORT_SEND_MINUTE,
    SCHEDULER_INTERVAL_MINUTES,
    SCHEDULER_MISFIRE_GRACE_TIME,
)
from app.core.logger import get_logger
from app.scheduler.jobs import collect_and_cluster_job, create_report_job, send_report_job

logger = get_logger(__name__)

_scheduler = BackgroundScheduler()


def start() -> None:
    if not settings.scheduler_enabled:
        logger.info("스케줄러 비활성화 (scheduler_enabled=False)")
        return

    _scheduler.add_job(collect_and_cluster_job, "interval", minutes=SCHEDULER_INTERVAL_MINUTES, id="collect_and_cluster")
    _scheduler.add_job(create_report_job, "cron", hour=REPORT_HOUR, minute=REPORT_CREATE_MINUTE, id="create_report", misfire_grace_time=SCHEDULER_MISFIRE_GRACE_TIME)
    _scheduler.add_job(send_report_job, "cron", hour=REPORT_HOUR, minute=REPORT_SEND_MINUTE, id="send_report", misfire_grace_time=SCHEDULER_MISFIRE_GRACE_TIME)
    _scheduler.start()
    logger.info(
        "스케줄러 시작 - collect/cluster interval=%dm, report cron=%02d:%02d/%02d:%02d",
        SCHEDULER_INTERVAL_MINUTES,
        REPORT_HOUR, REPORT_CREATE_MINUTE,
        REPORT_HOUR, REPORT_SEND_MINUTE,
    )


def stop() -> None:
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("스케줄러 종료")
