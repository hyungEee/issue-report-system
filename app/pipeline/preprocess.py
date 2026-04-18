from __future__ import annotations

from collections import Counter

from app.models.article import Article


def remove_duplicate_descriptions(articles: list[Article]) -> None:
    """2개 이상 기사에서 동일한 description이 등장하면 중복으로 보고 null 처리합니다."""
    desc_counts = Counter(a.description for a in articles if a.description)
    duplicates = {desc for desc, count in desc_counts.items() if count >= 2}
    for article in articles:
        if article.description in duplicates:
            article.description = None
