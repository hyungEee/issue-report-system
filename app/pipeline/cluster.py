from __future__ import annotations

import json
import math
from datetime import datetime, timedelta

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize
from sqlalchemy.orm import Session

from app.core.constants import ISSUE_OPEN
from app.core.logger import get_logger
from app.core.news_targets import SUPPORTED_CATEGORIES
from app.models.article import Article
from app.models.issue import Issue
from app.repositories.article_repo import ArticleRepository
from app.repositories.issue_repo import IssueRepository
from app.services.embedding_service import EmbeddingService

logger = get_logger(__name__)

_MERGE_THRESHOLD = 0.85  # 기존 이슈와 코사인 유사도 이상이면 병합


def _is_country_compatible(cluster_country: str, issue_country: str) -> bool:
    """클러스터와 기존 이슈의 country 병합 가능 여부.

    - 같은 나라끼리는 항상 병합 가능
    - 단일 국가 클러스터는 GLOBAL 이슈에 병합 가능 (글로벌 이슈 확장)
    - GLOBAL 클러스터는 단일 국가 이슈에 병합 불가
    """
    if cluster_country == issue_country:
        return True
    if cluster_country != "GLOBAL" and issue_country == "GLOBAL":
        return True
    return False


def run_clustering(
    db: Session,
    since_hours: int = 48,
    eps: float = 0.25,
    min_samples: int = 2,
) -> dict[str, int]:
    """
    미처리(issue_id 없는) 기사를 카테고리별로 군집화하여 Issue를 생성하거나
    기존 이슈에 병합합니다.

    eps:         코사인 거리 임계값 (낮을수록 엄격, 높을수록 느슨)
    min_samples: 클러스터 최소 기사 수 (이 미만이면 노이즈로 처리)
    since_hours: 최근 N시간 이내 기사만 대상
    """
    article_repo = ArticleRepository(db)
    issue_repo = IssueRepository(db)
    embedding_service = EmbeddingService()

    stats = {
        "categories_processed": 0,
        "clusters_found": 0,
        "issues_created": 0,
        "issues_merged": 0,
        "articles_linked": 0,
        "issues_closed": 0,
    }

    since = datetime.utcnow() - timedelta(hours=since_hours)

    for category in SUPPORTED_CATEGORIES:
        articles = list(article_repo.find_unlinked_articles(category=category, since=since, limit=1000))

        if len(articles) < min_samples:
            continue

        stats["categories_processed"] += 1

        embeddings = embedding_service.embed_articles(articles)
        normalized = normalize(embeddings)
        labels = DBSCAN(eps=eps, min_samples=min_samples, metric="euclidean").fit_predict(normalized)

        unique_labels = set(labels) - {-1}
        stats["clusters_found"] += len(unique_labels)

        existing_issues = list(issue_repo.find_open_with_centroid(category=category))

        for label in unique_labels:
            indices = np.where(labels == label)[0]
            cluster_articles = [articles[i] for i in indices]
            cluster_embeddings = normalized[indices]

            raw_centroid = cluster_embeddings.mean(axis=0)
            centroid = raw_centroid / np.linalg.norm(raw_centroid)

            cluster_countries = {a.country for a in cluster_articles}
            cluster_country = next(iter(cluster_countries)) if len(cluster_countries) == 1 else "GLOBAL"

            matched = _find_matching_issue(centroid, cluster_country, existing_issues)

            if matched:
                _merge_into_issue(matched, cluster_articles, cluster_embeddings, centroid)
                db.flush()
                stats["issues_merged"] += 1
                stats["articles_linked"] += len(cluster_articles)
            else:
                issue = _build_issue(cluster_articles, cluster_embeddings, centroid, category)
                issue_repo.save(issue)

                for article in cluster_articles:
                    article.issue_id = issue.id

                db.flush()
                stats["issues_created"] += 1
                stats["articles_linked"] += len(cluster_articles)

                existing_issues.append(issue)

        logger.info(
            "카테고리 군집화 완료 - category=%s articles=%d clusters=%d",
            category,
            len(articles),
            len(unique_labels),
        )

    cutoff = datetime.utcnow() - timedelta(hours=24)
    stats["issues_closed"] = issue_repo.close_stale_issues(cutoff)

    logger.info("전체 군집화 완료 - stats=%s", stats)
    return stats


def _find_matching_issue(centroid: np.ndarray, cluster_country: str, existing_issues: list[Issue]) -> Issue | None:
    """새 클러스터 centroid와 가장 유사한 기존 이슈를 반환. 임계값 미만이면 None."""
    valid = [
        (i, json.loads(i.centroid_json))
        for i in existing_issues
        if i.centroid_json and _is_country_compatible(cluster_country, i.country)
    ]
    if not valid:
        return None

    issues, centroids = zip(*valid)
    centroid_matrix = np.array(centroids)
    sims = centroid_matrix @ centroid
    best_idx = int(np.argmax(sims))

    if sims[best_idx] >= _MERGE_THRESHOLD:
        return issues[best_idx]
    return None


def _merge_into_issue(
    issue: Issue,
    new_articles: list[Article],
    new_embeddings: np.ndarray,
    new_centroid: np.ndarray,
) -> None:
    """기존 이슈에 새 기사를 병합하고 stats를 업데이트합니다."""
    for article in new_articles:
        article.issue_id = issue.id

    old_count = issue.article_count
    new_count = len(new_articles)
    total_count = old_count + new_count

    # centroid 재계산: 가중 평균 후 정규화
    old_centroid = np.array(json.loads(issue.centroid_json))
    raw = (old_centroid * old_count + new_centroid * new_count) / total_count
    updated_centroid = raw / np.linalg.norm(raw)

    issue.centroid_json = json.dumps(updated_centroid.tolist())
    issue.article_count = total_count
    issue.last_seen_at = max(a.published_at for a in new_articles)

    # importance_score 재계산
    all_articles = list(issue.articles) + new_articles
    all_sources = {a.source for a in all_articles}
    all_countries = {a.country for a in all_articles}
    issue.importance_score = round(
        len(all_articles)
        * len(all_sources)
        * math.log(len(all_countries) + 1),
        4,
    )

    # 대표 기사 갱신: 새 기사 중 업데이트된 centroid에 가장 가까운 기사가
    # 기존 대표 기사보다 centroid에 더 가까우면 교체
    new_sims = new_embeddings @ updated_centroid
    old_sim = float(old_centroid @ updated_centroid)
    best_new = _best_representative(new_articles, new_embeddings, updated_centroid)
    best_new_sim = float(new_sims[new_articles.index(best_new)])
    if _get_summary(best_new) and best_new_sim > old_sim:
        issue.representative_title = best_new.title
        issue.representative_summary = _get_summary(best_new)
        issue.representative_url = best_new.url


def _best_representative(articles: list[Article], embeddings: np.ndarray, centroid: np.ndarray) -> Article:
    """centroid에 가장 가까운 기사를 선택하되, description이 있는 기사를 우선합니다."""
    sims = embeddings @ centroid
    desc_indices = [i for i, a in enumerate(articles) if a.description]
    if desc_indices:
        best_i = max(desc_indices, key=lambda i: sims[i])
    else:
        best_i = int(np.argmax(sims))
    return articles[best_i]


def _get_summary(article: Article) -> str | None:
    return article.description or None


def _build_issue(
    articles: list[Article],
    embeddings: np.ndarray,
    centroid: np.ndarray,
    category: str,
) -> Issue:
    center_article = _best_representative(articles, embeddings, centroid)

    countries = {a.country for a in articles}
    country = next(iter(countries)) if len(countries) == 1 else "GLOBAL"

    importance_score = round(
        len(articles)
        * len({a.source for a in articles})
        * math.log(len(countries) + 1),
        4,
    )

    published_times = [a.published_at for a in articles]

    return Issue(
        representative_title=center_article.title,
        representative_summary=_get_summary(center_article),
        representative_url=center_article.url,
        country=country,
        category=category,
        importance_score=importance_score,
        article_count=len(articles),
        last_seen_at=max(published_times),
        centroid_json=json.dumps(centroid.tolist()),
        status=ISSUE_OPEN,
    )
