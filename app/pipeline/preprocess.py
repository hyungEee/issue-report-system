from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.logger import get_logger
from app.models.article import Article

logger = get_logger(__name__)

# 다국어 지원 경량 모델 (ko/ja/ar/he/pt/en/de/fr 등 50+ 언어)
_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        logger.info("임베딩 모델 로딩 - model=%s", _MODEL_NAME)
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def make_embedding_input(article: Article) -> str:
    parts = [article.title]
    if article.description:
        parts.append(article.description)
    return " ".join(parts)


def embed_articles(articles: list[Article]) -> np.ndarray:
    """
    Article 리스트를 받아 임베딩 행렬을 반환합니다.
    반환 shape: (len(articles), embedding_dim)
    """
    if not articles:
        return np.empty((0, 384))

    texts = [make_embedding_input(a) for a in articles]
    model = get_model()

    logger.info("임베딩 생성 시작 - article_count=%d", len(texts))
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    logger.info("임베딩 생성 완료")

    return embeddings
