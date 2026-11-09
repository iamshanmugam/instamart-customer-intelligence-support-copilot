from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import mock_llm
from src.common.paths import DATA_POLICIES, OUTPUTS_RAG, PROJECT_ROOT
from src.rag.embeddings import EmbeddingModel
from src.rag.vector_store import Chunk, InMemoryVectorStore
from src.ticket_triage.guardrails import mask_pii


def _load_policy_chunks() -> list[Chunk]:
    pol_dir = DATA_POLICIES if DATA_POLICIES.exists() else PROJECT_ROOT / "data" / "policies"
    chunks: list[Chunk] = []
    if not pol_dir.exists():
        return chunks
    for path in sorted(pol_dir.glob("*.txt")):
        text = path.read_text(encoding="utf-8")
        chunks.append(
            Chunk(
                chunk_id=path.stem,
                doc_id=path.name,
                title=path.stem.replace("_", " ").title(),
                text=text,
            )
        )
    return chunks


class RAGAssistant:
    def __init__(self) -> None:
        self.store = InMemoryVectorStore()
        self.embedder = EmbeddingModel()
        self._ready = False

    def build(self, _policy_df: pd.DataFrame | None = None) -> None:
        chunks = _load_policy_chunks()
        if not chunks:
            self._ready = False
            return
        texts = [c.text for c in chunks]
        vectors = self.embedder.fit_transform(texts)
        self.store.add(chunks, vectors)
        self.store.persist()
        self._ready = True

    def ask(self, question: str, top_k: int = 3) -> dict:
        question = mask_pii(question)
        if not self._ready:
            return {"answer": "RAG index not built.", "sources": [], "escalate": True}
        q_vec = self.embedder.transform([question])[0]
        hits = self.store.search(q_vec, top_k=top_k)
        if not hits:
            return {
                "answer": "No relevant policy found. Escalating to human agent.",
                "sources": [],
                "escalate": True,
            }
        context = "\n".join(f"[{c.title}.txt] {c.text}" for c, _ in hits)
        user_msg = f"CONTEXT:\n{context}\nQUESTION:\n{question}"
        messages = [
            {"role": "system", "content": "POLICY ASSISTANT"},
            {"role": "user", "content": user_msg},
        ]
        response = mock_llm.chat(messages)
        answer = response.choices[0].message.content or ""
        return {
            "answer": answer,
            "sources": [{"chunk_id": c.chunk_id, "title": c.title, "score": s} for c, s in hits],
            "escalate": False,
        }


def build_rag_from_policy(policy_df: pd.DataFrame) -> RAGAssistant:
    assistant = RAGAssistant()
    assistant.build(policy_df)
    return assistant


def run_sample_rag_queries(assistant: RAGAssistant) -> Path:
    samples = [
        "What delivery time makes a completed order eligible for a full refund?",
        "Who must approve a refund above INR 1000?",
        "How fast must a fraud ticket reach the security team?",
    ]
    OUTPUTS_RAG.mkdir(parents=True, exist_ok=True)
    results = [assistant.ask(q) for q in samples]
    path = OUTPUTS_RAG / "sample_rag_results.json"
    path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return path
