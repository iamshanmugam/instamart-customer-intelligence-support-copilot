from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable

from src.common.config import MAX_TICKET_CHARS, MAX_PROMPT_TOKENS

EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"\+?\d[\d\s\-]{8,}\d")
ORDER_RE = re.compile(r"\bORD-\d{6}\b", re.IGNORECASE)


@dataclass
class GuardrailResult:
    ok: bool
    reason: str = ""
    masked_text: str = ""
    estimated_tokens: int = 0


def mask_pii(text: str) -> str:
    out = EMAIL_RE.sub("[EMAIL_MASKED]", text)
    out = PHONE_RE.sub("[PHONE_MASKED]", out)
    out = ORDER_RE.sub("[ORDER_ID_MASKED]", out)
    return out


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


def apply_guardrails(text: str | None) -> GuardrailResult:
    if text is None:
        return GuardrailResult(ok=False, reason="empty_ticket")
    if not str(text).strip():
        return GuardrailResult(ok=False, reason="whitespace_only")
    if len(text) > MAX_TICKET_CHARS:
        return GuardrailResult(ok=False, reason="oversized_input")
    masked = mask_pii(text)
    tokens = estimate_tokens(masked)
    if tokens > MAX_PROMPT_TOKENS:
        return GuardrailResult(ok=False, reason="token_limit_exceeded")
    return GuardrailResult(ok=True, masked_text=masked, estimated_tokens=tokens)


def safe_llm_call(
    text: str,
    llm_callable: Callable[[str], str],
) -> tuple[bool, str, str]:
    """Returns (success, result_or_error, reason). Never calls LLM if guardrails fail."""
    gr = apply_guardrails(text)
    if not gr.ok:
        return False, "", gr.reason
    prompt = f"Classify the following support ticket.\nTicket:\n{gr.masked_text}"
    return True, llm_callable(prompt), ""
