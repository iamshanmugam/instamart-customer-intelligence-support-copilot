from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

import mock_llm
from src.common.paths import DATA_RAW, OUTPUTS_RAG


def _run_agent_message(message: str) -> str:
    messages = [{"role": "system", "content": "AGENT"}, {"role": "user", "content": message}]
    response = mock_llm.chat(messages, tools=[])
    msg = response.choices[0].message
    if msg.tool_calls:
        return f"TOOL:{msg.tool_calls[0].name}"
    return msg.content or ""


class RefundAgent:
    def __init__(self, rag=None) -> None:
        self.log_path = OUTPUTS_RAG / "simulated_refunds.jsonl"

    def process(self, order_id: str, reason: str) -> dict:
        text = f"{reason} Order {order_id}"
        if "fraud" in reason.lower() or "unauthorized" in reason.lower():
            return self._escalate("Fraud-related case requires human review.")
        content = _run_agent_message(text)
        eligible = content.startswith("REFUND:") or "REFUND:" in content
        result = {
            "status": "simulated_success" if eligible else "simulated_denied",
            "message": f"SIMULATION: {content}",
            "simulation": True,
        }
        self._log(result)
        return result

    def run_scenarios(self, path: Path | None = None) -> pd.DataFrame:
        path = path or DATA_RAW / "agent_scenarios.csv"
        if not path.exists():
            return pd.DataFrame()
        mock_llm.reset()
        df = pd.read_csv(path)
        rows = []
        for _, row in df.iterrows():
            content = _run_agent_message(str(row["message"]))
            rows.append(
                {
                    "scenario_id": row["scenario_id"],
                    "expected_outcome": row["expected_outcome"],
                    "agent_response": content[:200],
                }
            )
        out = pd.DataFrame(rows)
        OUTPUTS_RAG.mkdir(parents=True, exist_ok=True)
        out.to_csv(OUTPUTS_RAG / "agent_scenario_results.csv", index=False)
        return out

    def _escalate(self, reason: str) -> dict:
        out = {"status": "escalated", "message": reason, "simulation": True}
        self._log(out)
        return out

    def _log(self, record: dict) -> None:
        OUTPUTS_RAG.mkdir(parents=True, exist_ok=True)
        record = {**record, "logged_at": datetime.now(UTC).isoformat()}
        with self.log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
