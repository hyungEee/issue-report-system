from __future__ import annotations

from app.core.database import SessionLocal
from app.core.logger import get_logger
from app.pipeline.cluster import run_clustering
from app.pipeline.collect import collect_news
from app.pipeline.create_report import run_create_reports
from app.pipeline.send_report import run_send_reports

logger = get_logger(__name__)


def collect_and_cluster_job() -> None:
    with SessionLocal() as db:
        try:
            collect_stats = collect_news(db)
            db.commit()
            logger.info("collect 완료 - stats=%s", collect_stats)
        except Exception:
            db.rollback()
            logger.exception("collect 실패 - cluster 건너뜀")
            return

    with SessionLocal() as db:
        try:
            cluster_stats = run_clustering(db)
            db.commit()
            logger.info("cluster 완료 - stats=%s", cluster_stats)
        except Exception:
            db.rollback()
            logger.exception("cluster 실패")


def create_report_job() -> None:
    with SessionLocal() as db:
        try:
            stats = run_create_reports(db)
            db.commit()
            logger.info("create_report_job 완료 - stats=%s", stats)
        except Exception:
            db.rollback()
            logger.exception("create_report_job 실패")


def send_report_job() -> None:
    with SessionLocal() as db:
        try:
            stats = run_send_reports(db)
            db.commit()
            logger.info("send_report_job 완료 - stats=%s", stats)
        except Exception:
            db.rollback()
            logger.exception("send_report_job 실패")
