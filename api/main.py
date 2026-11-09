from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agents.refund_agent import RefundAgent
from src.common.paths import OUTPUTS_SEGMENTATION
from src.rag.assistant import RAGAssistant
from src.ticket_triage.classifier import classify_ticket

app = FastAPI(title="Instamart Support Co-Pilot API", version="1.0.0")

_rag: RAGAssistant | None = None


def _get_rag() -> RAGAssistant:
    global _rag
    if _rag is None:
        from src.data_foundation.load import load_raw_datasets
        from src.data_foundation.clean import clean_all_datasets

        _rag = RAGAssistant()
        pol_path = ROOT / "data" / "processed" / "policy_evaluation_clean.csv"
        if pol_path.exists():
            _rag.build(pd.read_csv(pol_path))
        else:
            raw = load_raw_datasets()
            cleaned = clean_all_datasets(raw)
            _rag.build(cleaned["policy"])
    return _rag


class TicketRequest(BaseModel):
    text: str = Field(min_length=1)
    strategy: str = "zero_shot"


class AskRequest(BaseModel):
    question: str = Field(min_length=1)


class RefundRequest(BaseModel):
    order_id: str
    reason: str = Field(min_length=1)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/customers/segments")
def customer_segments(limit: int = 50):
    path = OUTPUTS_SEGMENTATION / "customer_segments.csv"
    if not path.exists():
        raise HTTPException(404, "Run pipeline first (customer_segments.csv missing)")
    df = pd.read_csv(path).head(limit)
    return {"count": len(df), "data": df.to_dict(orient="records")}


@app.get("/customers/retention")
def retention_list(limit: int = 50):
    path = OUTPUTS_SEGMENTATION / "retention_list.csv"
    if not path.exists():
        raise HTTPException(404, "Run pipeline first")
    df = pd.read_csv(path).head(limit)
    return {"count": len(df), "data": df.to_dict(orient="records")}


@app.post("/tickets/classify")
def tickets_classify(req: TicketRequest):
    result = classify_ticket(req.text, strategy=req.strategy)
    if not result.get("success"):
        raise HTTPException(400, detail=result)
    return result


@app.post("/assistant/ask")
def assistant_ask(req: AskRequest):
    rag = _get_rag()
    return rag.ask(req.question)


@app.post("/refund/request")
def refund_request(req: RefundRequest):
    agent = RefundAgent(_get_rag())
    return agent.process(req.order_id.upper(), req.reason)
