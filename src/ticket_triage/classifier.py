from __future__ import annotations

import json

import pandas as pd

import mock_llm
from mock_llm import TransientLLMError
from src.common.paths import OUTPUTS_TICKET
from src.ticket_triage.guardrails import apply_guardrails
from src.ticket_triage.prompts import build_classify_messages
from src.ticket_triage.routing import assign_priority, assign_route


def _parse_category(content: str) -> str:
    if not content:
        return "technical"
    try:
        data = json.loads(content)
        return str(data.get("category", "technical")).lower()
    except json.JSONDecodeError:
        lower = content.lower()
        for cat in mock_llm.CATS:
            if cat in lower:
                return cat
        return "technical"


def _chat_classify(masked_ticket: str, few_shot: bool = False) -> str:
    messages = build_classify_messages(masked_ticket, few_shot=few_shot)
    for attempt in range(3):
        try:
            response = mock_llm.chat(messages)
            return response.choices[0].message.content or ""
        except TransientLLMError:
            if attempt == 2:
                raise
    return ""


def classify_ticket(text: str, strategy: str = "zero_shot", **_kwargs) -> dict:
    gr = apply_guardrails(text)
    if not gr.ok:
        return {
            "success": False,
            "rejected_reason": gr.reason,
            "llm_called": False,
        }
    raw = _chat_classify(gr.masked_text, few_shot=(strategy == "few_shot"))
    category = _parse_category(raw)
    return {
        "success": True,
        "category": category,
        "confidence": 0.5,
        "priority": assign_priority(category),
        "route": assign_route(category),
        "masked_ticket_preview": gr.masked_text[:200],
        "llm_called": True,
        "strategy": strategy,
        "raw_response_preview": raw[:120],
    }


def classify_tickets_batch(
    tickets: pd.DataFrame,
    text_col: str = "ticket_text",
    strategy: str = "zero_shot",
    limit: int | None = 50,
) -> pd.DataFrame:
    mock_llm.reset()
    subset = tickets.head(limit) if limit else tickets
    rows = []
    for _, row in subset.iterrows():
        col = text_col if text_col in row else "text"
        res = classify_ticket(row[col], strategy=strategy)
        rows.append(
            {
                "ticket_id": row.get("ticket_id"),
                "success": res.get("success"),
                "category": res.get("category"),
                "priority": res.get("priority"),
                "route": res.get("route"),
                "rejected_reason": res.get("rejected_reason"),
            }
        )
    out = pd.DataFrame(rows)
    OUTPUTS_TICKET.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUTS_TICKET / "classified_tickets.csv", index=False)
    return out
