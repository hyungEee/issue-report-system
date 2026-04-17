from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

from app.core.config import settings
from app.core.logger import get_logger
from app.core.news_targets import COUNTRY_LANG_MAP

logger = get_logger(__name__)


class NewsServiceError(Exception):
    pass


@dataclass
class RawNewsArticle:
    title: str
    description: str | None
    url: str
    source: str
    published_at: datetime
    country: str
    category: str
    language: str
    content: str | None = None
    source_url: str | None = None
    image_url: str | None = None


class NewsService:
    BASE_URL = "https://gnews.io/api/v4"

    def __init__(self) -> None:
        self.api_key = settings.gnews_api_key

    def fetch_top_headlines(
        self,
        *,
        country: str,
        category: str = "general",
        lang: str | None = None,
        max_results: int = 100,
        page: int = 1,
        from_date: str | None = None,
        to_date: str | None = None,
        q: str | None = None,
    ) -> list[RawNewsArticle]:
        """
        GNews top-headlines 조회.
        category / country / lang 은 요청 파라미터이며,
        응답 article 에는 category 필드가 없으므로
        호출 시 넘긴 category 값을 그대로 RawNewsArticle에 매핑한다.
        """
        if not self.api_key:
            raise NewsServiceError("GNEWS_API_KEY가 설정되지 않았습니다.")

        resolved_lang = lang or COUNTRY_LANG_MAP.get(country)

        params: dict[str, Any] = {
            "apikey": self.api_key,
            "country": country,
            "category": category,
            "max": max_results,
            "page": page,
        }

        if resolved_lang:
            params["lang"] = resolved_lang
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        if q:
            params["q"] = q

        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(f"{self.BASE_URL}/top-headlines", params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            logger.exception(
                "GNews HTTP 오류 - status=%s body=%s",
                e.response.status_code if e.response else "unknown",
                e.response.text if e.response else "no-response",
            )
            raise NewsServiceError(f"GNews HTTP 오류: {e}") from e
        except httpx.HTTPError as e:
            logger.exception("GNews 호출 실패")
            raise NewsServiceError(f"GNews 호출 실패: {e}") from e

        articles = data.get("articles", [])
        if not isinstance(articles, list):
            raise NewsServiceError("GNews 응답 형식이 올바르지 않습니다.")

        results: list[RawNewsArticle] = []
        for item in articles:
            mapped = self._map_gnews_article(
                item=item,
                country=country.upper(),
                category=category,
                language=resolved_lang or (item.get("lang") or "").lower(),
            )
            if mapped:
                results.append(mapped)

        return results

    def fetch_multi_country_top_headlines(
        self,
        *,
        countries: list[str],
        categories: list[str],
        max_results_per_call: int = 10,
    ) -> list[RawNewsArticle]:
        """
        여러 국가/카테고리 조합을 순회하여 수집.
        """
        all_articles: list[RawNewsArticle] = []

        for country in countries:
            for category in categories:
                try:
                    articles = self.fetch_top_headlines(
                        country=country,
                        category=category,
                        max_results=max_results_per_call,
                    )
                    all_articles.extend(articles)
                except NewsServiceError:
                    logger.exception(
                        "GNews 수집 실패 - country=%s, category=%s",
                        country,
                        category,
                    )
                    continue

        return all_articles

    def _map_gnews_article(
        self,
        *,
        item: dict[str, Any],
        country: str,
        category: str,
        language: str,
    ) -> RawNewsArticle | None:
        title = (item.get("title") or "").strip()
        url = item.get("url")
        published_at_raw = item.get("publishedAt")

        if not title or not url or not published_at_raw:
            return None

        source_info = item.get("source") or {}
        source_name = (source_info.get("name") or "unknown").strip()
        source_url = source_info.get("url")

        return RawNewsArticle(
            title=title,
            description=(item.get("description") or None),
            content=(item.get("content") or None),
            url=url,
            source=source_name,
            published_at=self._parse_iso_datetime(published_at_raw),
            country=country,
            category=category,
            language=language,
            source_url=source_url,
            image_url=item.get("image"),
        )

    @staticmethod
    def _parse_iso_datetime(value: str) -> datetime:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))