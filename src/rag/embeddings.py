from __future__ import annotations

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from src.common.config import EMBEDDING_BACKEND
from src.common.paths import DATA_KB, MODELS_DIR


class EmbeddingModel:
    def __init__(self) -> None:
        self.backend = EMBEDDING_BACKEND
        self._vectorizer: TfidfVectorizer | None = None
        self._st_model = None

    def fit_transform(self, texts: list[str]) -> np.ndarray:
        if self.backend == "sentence_transformers":
            try:
                from sentence_transformers import SentenceTransformer

                self._st_model = SentenceTransformer("all-MiniLM-L6-v2")
                return np.asarray(self._st_model.encode(texts, show_progress_bar=False))
            except Exception:
                self.backend = "sklearn"
        self._vectorizer = TfidfVectorizer(max_features=512, ngram_range=(1, 2))
        matrix = self._vectorizer.fit_transform(texts)
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._vectorizer, MODELS_DIR / "tfidf_vectorizer.joblib")
        return matrix.toarray()

    def transform(self, texts: list[str]) -> np.ndarray:
        if self._st_model is not None:
            return np.asarray(self._st_model.encode(texts, show_progress_bar=False))
        if self._vectorizer is None:
            path = MODELS_DIR / "tfidf_vectorizer.joblib"
            self._vectorizer = joblib.load(path)
        return self._vectorizer.transform(texts).toarray()
