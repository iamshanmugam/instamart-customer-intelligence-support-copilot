# Instamart Customer Intelligence & Support Co-Pilot

End-to-end Python project combining data cleaning, customer segmentation (RFM + K-Means), NLP ticket triage with guardrails, RAG policy assistant, and simulated refund workflows—using a **mock LLM** (no paid API keys).

## Business problem

Instamart needs clean customer/order/ticket data, actionable segments, automated complaint routing, and policy-grounded support—without exposing PII or processing real refunds.

## Key features

- Data foundation: clean CSVs, EDA charts, SQLite (`database/Instamart_DB.sqlite`)
- Segmentation: RFM, K-Means (K=2–8), PCA, `retention_list.csv`
- Ticket triage: categories, priority, routing, PII masking, zero/few-shot via mock LLM
- RAG + refund agent (simulation only)
- FastAPI + optional Streamlit UI
- Pytest suite and `run_project.py` pipeline

**Data note:** No instructor CSVs were present; raw data is **synthetic** from `generate_data.py`.

## Quick start (Windows)

```powershell
cd "C:\My AI Projects\Instamart-Customer-Intelligence-Support-Copilot"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_project.py
pytest -q
```

## Run API and UI

```powershell
uvicorn api.main:app --reload
streamlit run frontend/app.py
```

## Project structure

| Path | Purpose |
|------|---------|
| `src/data_foundation/` | Load, clean, EDA |
| `src/customer_analytics/` | RFM, K-Means, PCA |
| `src/ticket_triage/` | Guardrails, classification |
| `src/rag/`, `src/agents/` | RAG, order lookup, refund sim |
| `outputs/` | Charts, segments, triage, RAG samples |
| `docs/` | Technical, API, testing guides |

## Limitations

- No genuine churn label → no supervised churn metrics (see `outputs/segmentation/churn_modelling_report.md`)
- Mock LLM only by default; configure real providers via `.env` when ready
- Refunds are **simulated**; never real payments

## Git branches (submission)

```powershell
git init
git checkout -b main
git checkout -b part-a-data-foundation
git checkout -b part-b-customer-segmentation
git checkout -b part-c-ticket-triage
git checkout -b part-d-rag-assistant
git checkout main
```

See `LEARNING_GUIDE.md` for step-by-step learning (English + Tamil notes) and `PROJECT_COMPLETION_REPORT.md` after running the pipeline.

**Readable HTML:** open [`docs/PROJECT_DOCUMENT.html`](docs/PROJECT_DOCUMENT.html) in your browser (or double-click the file in File Explorer).
