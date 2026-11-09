from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    RecursiveCharacterTextSplitter = None  # type: ignore

from mock_llm import get_llm
from src.common.paths import OUTPUTS_RAG
from src.rag.embeddings import EmbeddingModel
from src.rag.knowledge_base import load_policy_documents, save_knowledge_base
from src.rag.vector_store import Chunk, InMemoryVectorStore
from src.ticket_triage.guardrails import mask_pii


def _split_text(text: str) -> list[str]:
    if RecursiveCharacterTextSplitter:
        splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
        return splitter.split_text(text)
    size = 400
    return [text[i : i + size] for i in range(0, len(text), size - 50)] or [text]


class RAGAssistant:
    def __init__(self) -> None:
        self.store = InMemoryVectorStore()
        self.embedder = EmbeddingModel()
        self.llm = get_llm()
        self._ready = False

    def build(self, policy_df: pd.DataFrame) -> None:
        docs = load_policy_documents(policy_df)
        save_knowledge_base(docs)
        chunks: list[Chunk] = []
        texts: list[str] = []
        for doc in docs:
            for i, piece in enumerate(_split_text(doc["text"])):
                cid = f"{doc['id']}_{i}"
                chunks.append(Chunk(cid, doc["id"], doc["title"], piece))
                texts.append(piece)
        vectors = self.embedder.fit_transform(texts)
        self.store.add(chunks, vectors)
        self.store.persist()
        self._ready = True

    def load_index(self) -> None:
        self.store.load()
        if self.store.chunks and self.store.vectors is not None:
            self._ready = True

    def ask(self, question: str, top_k: int = 3) -> dict:
        question = mask_pii(question)
        if not self._ready:
            return {"answer": "RAG index not built.", "sources": [], "escalate": True}
        if not self.store.chunks or self.store.vectors is None:
            return {
                "answer": "No relevant policy found. Escalating to human agent.",
                "sources": [],
                "escalate": True,
            }
        q_vec = self.embedder.transform([question])[0]
        hits = self.store.search(q_vec, top_k=top_k)
        if not hits:
            return {
                "answer": "No relevant policy found. Escalating to human agent.",
                "sources": [],
                "escalate": True,
            }
        context = "\n\n".join(f"[{c.title}] {c.text}" for c, _ in hits)
        prompt = f"Question: {question}\nContext:\n{context}"
        answer = self.llm.complete(prompt, mode="rag", context=context)
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
        "Can I get a refund for a damaged item?",
        "My delivery is delayed by 2 hours.",
        "Someone used my account fraudulently.",
    ]
    OUTPUTS_RAG.mkdir(parents=True, exist_ok=True)
    results = [assistant.ask(q) for q in samples]
    path = OUTPUTS_RAG / "sample_rag_results.json"
    path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return path
