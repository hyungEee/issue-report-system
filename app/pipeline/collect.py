from __future__ import annotations

import hashlib
import time
from collections.abc import Iterable
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.core.news_targets import CORE_COUNTRIES, SUPPORTED_CATEGORIES
from app.models.article import Article
from app.repositories.article_repo import ArticleRepository
from app.services.news_service import NewsService, NewsServiceError, RawNewsArticle

logger = get_logger(__name__)

DEFAULT_CATEGORIES = SUPPORTED_CATEGORIES


def collect_news(
    db: Session,
    countries: list[str] | None = None,
    categories: list[str] | None = None,
    max_results_per_call: int = 100,
    max_pages: int = 1,
    delay_between_calls: float = 1.5,
) -> dict[str, int]:
    """
    GNews로부터 여러 국가/카테고리 헤드라인을 수집하고
    중복 제거 후 Article 테이블에 저장합니다.

    return 예시:
    {
        "requested": 24,
        "fetched": 180,
        "saved": 120,
        "skipped_url_duplicate": 40,
        "skipped_dedup_duplicate": 20,
        "failed_calls": 2,
    }
    """
    news_service = NewsService()
    article_repo = ArticleRepository(db)

    target_countries = countries or CORE_COUNTRIES
    target_categories = categories or DEFAULT_CATEGORIES

    stats = {
        "requested": 0,
        "fetched": 0,
        "saved": 0,
        "skipped_url_duplicate": 0,
        "skipped_dedup_duplicate": 0,
        "failed_calls": 0,
    }

    for country in target_countries:
        for category in target_categories:
            for page in range(1, max_pages + 1):
                stats["requested"] += 1

                try:
                    raw_articles = news_service.fetch_top_headlines(
                        country=country,
                        category=category,
                        max_results=max_results_per_call,
                        page=page,
                    )
                except NewsServiceError as e:
                    stats["failed_calls"] += 1
                    logger.exception(
                        "뉴스 수집 실패 - country=%s category=%s page=%d error=%s",
                        country,
                        category,
                        page,
                        e,
                    )
                    time.sleep(delay_between_calls)
                    break

                time.sleep(delay_between_calls)
                stats["fetched"] += len(raw_articles)

                for raw in raw_articles:
                    if article_repo.exists_by_url(raw.url):
                        stats["skipped_url_duplicate"] += 1
                        continue

                    article = to_article_model(raw)

                    if article_repo.exists_by_dedup_key(article.dedup_key):
                        stats["skipped_dedup_duplicate"] += 1
                        continue

                    article_repo.save(article)
                    stats["saved"] += 1

                # 결과가 max보다 적으면 다음 페이지 없음
                if len(raw_articles) < max_results_per_call:
                    break

    logger.info("뉴스 수집 완료 - stats=%s", stats)
    return stats


def to_article_model(raw: RawNewsArticle) -> Article:
    return Article(
        title=normalize_text(raw.title),
        description=normalize_nullable_text(raw.description),
        content=raw.content or None,
        url=normalize_url(raw.url),
        source=normalize_text(raw.source),
        published_at=normalize_datetime(raw.published_at),
        country=raw.country.upper(),
        category=raw.category.lower(),
        dedup_key=make_dedup_key(raw),
        created_at=datetime.now(timezone.utc),
    )


def make_dedup_key(raw: RawNewsArticle) -> str:
    """
    같은 이슈/같은 기사 중복을 너무 빡빡하지 않게 잡기 위한 키.

    URL은 매체별로 달라질 수 있으므로 포함하지 않고,
    title + source + published hour 정도로 구성합니다.
    """
    normalized_title = normalize_text(raw.title).lower()
    normalized_source = normalize_text(raw.source).lower()
    published_hour = normalize_datetime(raw.published_at).strftime("%Y-%m-%d-%H")

    base = f"{normalized_title}|{normalized_source}|{published_hour}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def normalize_text(value: str) -> str:
    return " ".join((value or "").strip().split())


def normalize_nullable_text(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = " ".join(value.strip().split())
    return normalized or None


def normalize_url(value: str) -> str:
    return (value or "").strip()


def normalize_datetime(value: datetime) -> datetime:
    """
    timezone-aware datetime 으로 통일합니다.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)