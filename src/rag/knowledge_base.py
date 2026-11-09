from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.common.paths import DATA_KB


def load_policy_documents(policy_df: pd.DataFrame) -> list[dict]:
    docs = []
    for _, row in policy_df.iterrows():
        text = f"{row.get('policy_title', '')}\n{row.get('policy_text', '')}"
        docs.append(
            {
                "id": row.get("policy_id", ""),
                "title": row.get("policy_title", ""),
                "category": row.get("category", ""),
                "text": text.strip(),
            }
        )
    return docs


def save_knowledge_base(docs: list[dict]) -> Path:
    DATA_KB.mkdir(parents=True, exist_ok=True)
    path = DATA_KB / "policies.txt"
    lines = []
    for d in docs:
        lines.append(f"=== {d['id']} | {d['title']} ===\n{d['text']}\n")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
