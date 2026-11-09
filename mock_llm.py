"""
Mock LLM — deterministic responses without paid API keys.
Swap via LLM_PROVIDER in .env when a real provider is configured.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from abc import ABC, abstractmethod
from typing import Any

from dotenv import load_dotenv

from src.common.config import TICKET_CATEGORIES

load_dotenv()

CATEGORY_KEYWORDS = {
    "Refund": ["refund", "money back", "return", "damaged"],
    "Delivery Delay": ["delay", "late", "not delivered", "waiting"],
    "Payment": ["payment", "debit", "failed", "charged twice"],
    "Fraud": ["fraud", "suspicious", "unauthorized", "hacked"],
    "Product Quality": ["quality", "expired", "rotten", "poor"],
    "App Issue": ["app", "crash", "login", "bug"],
}


class BaseLLM(ABC):
    @abstractmethod
    def complete(self, prompt: str, **kwargs: Any) -> str:
        ...


class MockLLM(BaseLLM):
    """Rule + hash-based responses for classification, RAG, and refund simulation."""

    def complete(self, prompt: str, **kwargs: Any) -> str:
        mode = kwargs.get("mode", "generic")
        if mode == "zero_shot_classify":
            return self._classify(prompt, use_examples=False)
        if mode == "few_shot_classify":
            return self._classify(prompt, use_examples=True)
        if mode == "rag":
            return self._rag_answer(prompt, kwargs.get("context", ""))
        if mode == "refund":
            return self._refund_decision(prompt, kwargs.get("context", ""))
        return self._generic(prompt)

    def _extract_ticket(self, prompt: str) -> str:
        m = re.search(r"Ticket:\s*(.+)", prompt, re.DOTALL | re.IGNORECASE)
        return (m.group(1).strip() if m else prompt).lower()

    def _classify(self, prompt: str, use_examples: bool) -> str:
        text = self._extract_ticket(prompt)
        scores = {cat: 0 for cat in TICKET_CATEGORIES}
        for cat, keys in CATEGORY_KEYWORDS.items():
            for k in keys:
                if k in text:
                    scores[cat] += 2 if use_examples else 1
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            best = "Other"
        payload = {"category": best, "confidence": min(0.95, 0.55 + scores[best] * 0.1)}
        return json.dumps(payload)

    def _rag_answer(self, prompt: str, context: str) -> str:
        if not context.strip():
            return (
                "I could not find a specific policy section for your question. "
                "Please contact support or escalate to a human agent."
            )
        snippet = context.strip()[:500]
        q = prompt[-200:]
        return (
            f"Based on Instamart policy context: {snippet}\n\n"
            f"Answer (simulated): This guidance applies to your question about '{q[:80]}...'. "
            "For edge cases, escalate to a human agent."
        )

    def _refund_decision(self, prompt: str, context: str) -> str:
        lower = prompt.lower() + context.lower()
        if "fraud" in lower:
            return json.dumps(
                {
                    "eligible": False,
                    "action": "escalate_human",
                    "reason": "Fraud-related case requires human review.",
                }
            )
        if "24 hours" in context.lower() and "damaged" in lower:
            eligible = True
        elif "partial" in context.lower() and "quality" in lower:
            eligible = True
        else:
            eligible = "refund" in lower and "delivered" not in lower
        return json.dumps(
            {
                "eligible": eligible,
                "action": "simulate_refund" if eligible else "deny_or_review",
                "reason": "Simulated policy check (not a real payment).",
            }
        )

    def _generic(self, prompt: str) -> str:
        h = hashlib.sha256(prompt.encode()).hexdigest()[:8]
        return f"[Mock LLM response {h}] Processed request safely."


def get_llm() -> BaseLLM:
    provider = os.getenv("LLM_PROVIDER", "mock").lower()
    if provider == "mock":
        return MockLLM()
    raise NotImplementedError(
        f"Provider '{provider}' is not configured. Use LLM_PROVIDER=mock or extend get_llm()."
    )
