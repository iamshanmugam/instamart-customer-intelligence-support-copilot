from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from mock_llm import get_llm
from src.agents.order_lookup import lookup_order
from src.common.paths import OUTPUTS_RAG
from src.rag.assistant import RAGAssistant
from src.ticket_triage.guardrails import mask_pii


class RefundAgent:
    def __init__(self, rag: RAGAssistant | None = None) -> None:
        self.rag = rag
        self.llm = get_llm()
        self.log_path = OUTPUTS_RAG / "simulated_refunds.jsonl"

    def process(self, order_id: str, reason: str) -> dict:
        reason_safe = mask_pii(reason)
        if "fraud" in reason_safe.lower():
            return self._escalate("Fraud-related case requires human review.")
        order = lookup_order(order_id)
        if not order.get("found"):
            return {
                "status": "failed",
                "decision": "escalate_human",
                "message": "Order not found or invalid ID.",
                "simulation": True,
            }

        policy_ctx = ""
        if self.rag:
            rag_res = self.rag.ask(f"Refund policy for: {reason_safe}")
            policy_ctx = rag_res.get("answer", "")
            if rag_res.get("escalate") and "fraud" in reason_safe.lower():
                return self._escalate("Fraud or missing policy — human review required.")

        prompt = f"Order: {order['order_id']} status={order['order_status']}. Reason: {reason_safe}"
        raw = self.llm.complete(prompt, mode="refund", context=policy_ctx)
        try:
            decision = json.loads(raw)
        except json.JSONDecodeError:
            decision = {"eligible": False, "action": "escalate_human", "reason": "parse_error"}

        if decision.get("action") == "escalate_human" or "fraud" in reason_safe.lower():
            return self._escalate(decision.get("reason", "Escalated"))

        eligible = bool(decision.get("eligible"))
        result = {
            "status": "simulated_success" if eligible else "simulated_denied",
            "decision": decision.get("action"),
            "eligible": eligible,
            "message": (
                "SIMULATION: Refund recorded (no real payment processed)."
                if eligible
                else "SIMULATION: Refund not approved; review policy."
            ),
            "order": {k: v for k, v in order.items() if k != "found"},
            "simulation": True,
        }
        self._log(result)
        return result

    def _escalate(self, reason: str) -> dict:
        out = {
            "status": "escalated",
            "decision": "escalate_human",
            "message": reason,
            "simulation": True,
        }
        self._log(out)
        return out

    def _log(self, record: dict) -> None:
        OUTPUTS_RAG.mkdir(parents=True, exist_ok=True)
        record = {**record, "logged_at": datetime.now(UTC).isoformat()}
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
