# Testing Guide

## Run all tests

```powershell
.\.venv\Scripts\pytest -q
```

## Structure

| File | Coverage |
|------|----------|
| `tests/test_data_foundation.py` | CSV load errors, cleaning |
| `tests/test_guardrails.py` | Empty/oversized/PII, LLM skip |
| `tests/test_rfm.py` | Zero completed orders |
| `tests/test_rag_refund.py` | RAG fallback, fraud escalation |

## Mock LLM

Tests use `mock_llm.MockLLM` via `get_llm()` — no API keys.

## Last verified run

**13 passed** (see `PROJECT_COMPLETION_REPORT.md`).
