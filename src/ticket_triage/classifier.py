from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from mock_llm import get_llm
from src.common.paths import OUTPUTS_TICKET
from src.ticket_triage.guardrails import apply_guardrails
from src.ticket_triage.prompts import few_shot_prompt, zero_shot_prompt
from src.ticket_triage.routing import assign_priority, assign_route


def _parse_llm_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"category": "Other", "confidence": 0.3}


def classify_ticket(
    text: str,
    strategy: str = "zero_shot",
    llm=None,
) -> dict:
    llm = llm or get_llm()
    gr = apply_guardrails(text)
    if not gr.ok:
        return {
            "success": False,
            "rejected_reason": gr.reason,
            "llm_called": False,
        }

    mode = "few_shot_classify" if strategy == "few_shot" else "zero_shot_classify"
    prompt = (
        few_shot_prompt(gr.masked_text)
        if strategy == "few_shot"
        else zero_shot_prompt(gr.masked_text)
    )

    result = llm.complete(prompt, mode=mode)
    parsed = _parse_llm_json(result)
    category = parsed.get("category", "Other")
    priority = assign_priority(category)
    route = assign_route(category)
    return {
        "success": True,
        "category": category,
        "confidence": parsed.get("confidence", 0.5),
        "priority": priority,
        "route": route,
        "masked_ticket_preview": gr.masked_text[:200],
        "llm_called": True,
        "strategy": strategy,
    }


def classify_tickets_batch(
    tickets: pd.DataFrame,
    text_col: str = "ticket_text",
    strategy: str = "zero_shot",
    limit: int | None = 50,
) -> pd.DataFrame:
    llm = get_llm()
    subset = tickets.head(limit) if limit else tickets
    rows = []
    for _, row in subset.iterrows():
        res = classify_ticket(row[text_col], strategy=strategy, llm=llm)
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
