from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.common.paths import DATA_KB


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    text: str


class InMemoryVectorStore:
    def __init__(self) -> None:
        self.chunks: list[Chunk] = []
        self.vectors: np.ndarray | None = None

    def add(self, chunks: list[Chunk], vectors: np.ndarray) -> None:
        self.chunks = chunks
        self.vectors = vectors

    def search(self, query_vector: np.ndarray, top_k: int = 3) -> list[tuple[Chunk, float]]:
        if self.vectors is None or len(self.chunks) == 0:
            return []
        q = query_vector.reshape(1, -1)
        sims = cosine_similarity(q, self.vectors).flatten()
        idx = np.argsort(-sims)[:top_k]
        return [(self.chunks[i], float(sims[i])) for i in idx if sims[i] > 0.05]

    def persist(self, path: Path | None = None) -> Path:
        path = path or DATA_KB / "vector_index.json"
        DATA_KB.mkdir(parents=True, exist_ok=True)
        payload = {
            "chunks": [c.__dict__ for c in self.chunks],
            "vectors": self.vectors.tolist() if self.vectors is not None else [],
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def load(self, path: Path | None = None) -> None:
        path = path or DATA_KB / "vector_index.json"
        if not path.exists():
            return
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.chunks = [Chunk(**c) for c in payload["chunks"]]
        self.vectors = np.array(payload["vectors"]) if payload["vectors"] else None
