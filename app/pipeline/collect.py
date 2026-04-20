from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.constants import DESCRIPTION_FALLBACK_LENGTH, MIN_DESCRIPTION_LENGTH
from app.core.logger import get_logger
from app.core.news_targets import CATEGORY_MAX_PAGES, COUNTRY_MAX_PAGES, SUPPORTED_CATEGORIES, SUPPORTED_COUNTRIES
from app.models.article import Article
from app.repositories.article_repo import ArticleRepository
from app.services.news_service import NewsService, NewsServiceError, RawNewsArticle

logger = get_logger(__name__)


def collect_news(
    db: Session,
    countries: list[str] | None = None,
    categories: list[str] | None = None,
    max_results_per_call: int = 100,
    max_pages: int = 1,
) -> dict[str, int]:
    """
    GNews로부터 여러 국가/카테고리 헤드라인을 수집하고
    중복 제거 후 Article 테이블에 저장합니다.

    return 예시:
    {
        "requested": 24,
        "fetched": 180,
        "saved": 120,
        "skipped_dedup_duplicate": 20,
        "failed_calls": 2,
    }
    """
    news_service = NewsService()
    article_repo = ArticleRepository(db)

    target_countries = countries or SUPPORTED_COUNTRIES
    target_categories = categories or SUPPORTED_CATEGORIES

    stats = {
        "requested": 0,
        "fetched": 0,
        "saved": 0,
        "skipped_dedup_duplicate": 0,
        "failed_calls": 0,
    }

    for country in target_countries:
        country_pages = COUNTRY_MAX_PAGES.get(country, max_pages)
        for category in target_categories:
            pages = min(country_pages, CATEGORY_MAX_PAGES.get(category, max_pages))
            for page in range(1, pages + 1):
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
                    break

                stats["fetched"] += len(raw_articles)

                _save_batch(raw_articles, article_repo, stats)

                if len(raw_articles) < max_results_per_call:
                    break

    logger.info("뉴스 수집 완료 - stats=%s", stats)
    return stats


def _save_batch(
    raw_articles: list[RawNewsArticle],
    article_repo: ArticleRepository,
    stats: dict[str, int],
) -> None:
    candidate_keys = [_make_dedup_key(raw) for raw in raw_articles]
    seen_keys = article_repo.get_existing_dedup_keys(candidate_keys)

    for raw, dedup_key in zip(raw_articles, candidate_keys):
        if dedup_key in seen_keys:
            stats["skipped_dedup_duplicate"] += 1
            continue

        article_repo.save(_to_article_model(raw, dedup_key))
        stats["saved"] += 1
        seen_keys.add(dedup_key)


def _to_article_model(raw: RawNewsArticle, dedup_key: str) -> Article:
    content = raw.content or None
    description = _normalize_nullable_text(raw.description)
    if not description or len(description) <= MIN_DESCRIPTION_LENGTH:
        description = content[:DESCRIPTION_FALLBACK_LENGTH] if content else None

    return Article(
        title=_normalize_text(raw.title),
        description=description,
        content=content,
        url=_normalize_url(raw.url),
        source=_normalize_text(raw.source),
        published_at=_normalize_datetime(raw.published_at),
        country=raw.country,
        category=raw.category.lower(),
        dedup_key=dedup_key,
    )


def _make_dedup_key(raw: RawNewsArticle) -> str:
    """
    같은 이슈/같은 기사 중복을 너무 빡빡하지 않게 잡기 위한 키.

    URL은 매체별로 달라질 수 있으므로 포함하지 않고,
    title + source + published hour 정도로 구성합니다.
    """
    normalized_title = _normalize_text(raw.title).lower()
    normalized_source = _normalize_text(raw.source).lower()
    published_hour = _normalize_datetime(raw.published_at).strftime("%Y-%m-%d-%H")

    base = f"{normalized_title}|{normalized_source}|{published_hour}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def _normalize_text(value: str) -> str:
    return " ".join((value or "").strip().split())


def _normalize_nullable_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = " ".join(value.strip().split())
    return normalized or None


def _normalize_url(value: str) -> str:
    return (value or "").strip()


def _normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
