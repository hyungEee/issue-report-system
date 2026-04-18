from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.logger import get_logger
from app.models.article import Article

logger = get_logger(__name__)

_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


class EmbeddingService:
    _model: SentenceTransformer | None = None

    def _get_model(self) -> SentenceTransformer:
        if EmbeddingService._model is None:
            logger.info("임베딩 모델 로딩 - model=%s", _MODEL_NAME)
            EmbeddingService._model = SentenceTransformer(_MODEL_NAME)
        return EmbeddingService._model

    def embed_articles(self, articles: list[Article]) -> np.ndarray:
        if not articles:
            return np.empty((0, 384))

        texts = [self._make_embedding_input(a) for a in articles]
        model = self._get_model()

        logger.info("임베딩 생성 시작 - article_count=%d", len(texts))
        embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        logger.info("임베딩 생성 완료")

        return embeddings

    @staticmethod
    def _make_embedding_input(article: Article) -> str:
        parts = [article.title]
        if article.description:
            parts.append(article.description)
        return " ".join(parts)
