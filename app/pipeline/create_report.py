from __future__ import annotations

import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logger import get_logger
from app.models.issue import Issue
from app.models.report import Report
from app.repositories.issue_repo import IssueRepository
from app.repositories.report_repo import ReportRepository
from app.repositories.user_setting_repo import UserSettingRepository
from app.services.llm_service import IssueDigest, LLMService

logger = get_logger(__name__)

_CATEGORY_KO = {
    "world":         "국제정세",
    "nation":        "정치/사회",
    "business":      "비즈니스",
    "technology":    "기술",
    "entertainment": "엔터테인먼트",
    "sports":        "스포츠",
    "science":       "과학",
}


def run_create_reports(db: Session) -> dict[str, int]:
    """모든 유저에 대해 일간 리포트를 생성하고 PENDING 상태로 저장합니다."""
    user_repo = UserSettingRepository(db)
    issue_repo = IssueRepository(db)
    report_repo = ReportRepository(db)
    llm_service = LLMService()

    stats = {"users_processed": 0, "reports_created": 0}

    for user in user_repo.find_all():
        categories = json.loads(user.category_json) if user.category_json else None

        issues = list(issue_repo.find_for_report(
            category_list=categories,
            limit=settings.report_top_n,
        ))

        if not issues:
            logger.info("리포트 대상 이슈 없음 - user_id=%s", user.user_id)
            stats["users_processed"] += 1
            continue

        content = _build_report_content(issues, llm_service)

        report_repo.save(Report(user_id=user.user_id, content=content))

        stats["reports_created"] += 1
        stats["users_processed"] += 1

    logger.info("리포트 생성 완료 - stats=%s", stats)
    return stats


def _build_report_content(issues: list[Issue], llm_service: LLMService) -> str:
    report_date = datetime.now(timezone.utc).date()
    blocks: list[str] = [
        f"<h2>{report_date.strftime('%Y년 %m월 %d일')} 주요 이슈 리포트</h2>",
        "<hr>",
    ]

    for rank, issue in enumerate(issues, start=1):
        rep_article = next(
            (a for a in issue.articles if a.url == issue.representative_url),
            None,
        )
        title = rep_article.title if rep_article else issue.representative_title
        content = rep_article.content if rep_article else None

        try:
            digest = llm_service.summarize_issue(title, content)
        except Exception:
            logger.exception("LLM 요약 실패 - issue_id=%s", issue.id)
            digest = IssueDigest(
                title_ko=title,
                summary=issue.representative_summary or issue.representative_title,
                insight="",
            )

        category_ko = _CATEGORY_KO.get(issue.category, issue.category)
        blocks.append(f"<h3>{rank}. [{category_ko}] {digest.title_ko}</h3>")
        blocks.append(f"<p>{digest.summary}</p>")
        if digest.insight:
            blocks.append(f"<p><em>{digest.insight}</em></p>")
        if issue.representative_url:
            blocks.append(f'<p><a href="{issue.representative_url}">기사 보기</a></p>')
        blocks.append("<hr>")

    return "\n".join(blocks)
