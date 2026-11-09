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
    policy = pd.DataFrame(
        [{"policy_id": "P1", "policy_title": "Fraud", "policy_text": "Fraud policy", "category": "Fraud"}]
    )
    rag = RAGAssistant()
    rag.build(policy)
    agent = RefundAgent(rag)
    out = agent.process("ORD999999", "fraudulent charge")
    assert out["decision"] == "escalate_human" or out.get("status") == "escalated"


def test_lookup_invalid_order():
    assert lookup_order("BAD")["found"] is False
