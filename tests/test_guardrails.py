from unittest.mock import MagicMock

from src.ticket_triage.guardrails import apply_guardrails, mask_pii, safe_llm_call


def test_empty_rejected():
    r = apply_guardrails("")
    assert not r.ok
    assert r.reason == "whitespace_only"


def test_whitespace_rejected():
    r = apply_guardrails("   \n\t  ")
    assert not r.ok


def test_oversized_rejected(monkeypatch):
    monkeypatch.setattr("src.ticket_triage.guardrails.MAX_TICKET_CHARS", 10)
    r = apply_guardrails("x" * 20)
    assert r.reason == "oversized_input"


def test_pii_masked():
    text = "Email user@test.com phone +919876543210 order ORD-100001"
    masked = mask_pii(text)
    assert "user@test.com" not in masked
    assert "ORD-100001" not in masked


def test_rejected_never_calls_llm():
    llm = MagicMock()
    ok, _, reason = safe_llm_call("", llm)
    assert not ok
    llm.assert_not_called()


def test_valid_classification_calls_llm():
    llm = MagicMock(return_value='{"category":"Refund"}')
    ok, res, _ = safe_llm_call("I need a refund", llm)
    assert ok
    llm.assert_called_once()
