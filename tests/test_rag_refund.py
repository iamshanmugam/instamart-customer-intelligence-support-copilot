import pandas as pd

from src.rag.assistant import RAGAssistant
from src.agents.refund_agent import RefundAgent
from src.agents.order_lookup import lookup_order


def test_rag_no_context_escalates():
    assistant = RAGAssistant()
    assistant._ready = True
    assistant.store.chunks = []
    assistant.store.vectors = None
    res = assistant.ask("random question")
    assert res["escalate"] is True


def test_refund_fraud_escalates():
    agent = RefundAgent()
    out = agent.process("ORD-100001", "fraudulent unauthorized charge")
    assert out.get("status") == "escalated"


def test_lookup_invalid_order():
    assert lookup_order("BAD")["found"] is False
