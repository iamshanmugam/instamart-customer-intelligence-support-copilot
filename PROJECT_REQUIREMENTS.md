# Project Requirements — Instamart Customer Intelligence & Support Co-Pilot

## Business objective

Build an integrated system for Swiggy Instamart that:

1. Cleans and stores customer, order, and support ticket data.
2. Segments customers via RFM and K-Means clustering.
3. Identifies at-risk customers for retention (behavioural, not fabricated supervised churn).
4. Classifies support tickets with NLP, guardrails, and PII masking.
5. Answers policy questions via RAG and simulates refund workflows safely.

## Assignment requirements (summary)

| Area | Requirement |
|------|-------------|
| Part A | Load, clean, EDA, SQLite |
| Part B | RFM, StandardScaler, K-Means (K=2–8), PCA, segments, retention list |
| Part B (conditional) | Logistic Regression / Random Forest only if genuine churn label exists |
| Part C | Ticket categories, priority, routing, guardrails, zero/few-shot, mock LLM |
| Part D | RAG, vector store, order lookup, simulated refund agent |
| App | FastAPI + simple UI (Streamlit) |
| Quality | Pytest, `run_project.py`, notebook, documentation |

## Input datasets

| File | Location | Source |
|------|----------|--------|
| `customers.csv` | `data/raw/` | Synthetic via `generate_data.py` (no instructor bundle in repo) |
| `orders.csv` | `data/raw/` | Synthetic |
| `support_tickets.csv` | `data/raw/` | Synthetic |
| `policy_evaluation.csv` | `data/raw/` | Synthetic policy Q&A for RAG evaluation |

**Note:** No `instructor-materials/` were present at discovery. All raw data is locally generated and documented as synthetic.

## Expected outputs

- `data/processed/*.csv` — cleaned datasets
- `database/Instamart_DB.sqlite` — relational store
- `outputs/eda/` — charts
- `outputs/segmentation/` — RFM, K evaluation, PCA, `customer_segments.csv`, `retention_list.csv`
- `outputs/ticket_triage/` — classified tickets
- `outputs/rag/` — sample RAG results
- `models/` — scaler, K-Means joblib files
- Reports under `outputs/`

## Technology stack

Python 3.11+, Pandas, NumPy, SQLite, Matplotlib, Seaborn, scikit-learn, Joblib, FastAPI, Pydantic, Streamlit, LangChain (text splitters), pytest; mock LLM (no paid API required).

## Implementation phases

0. Discovery and planning (this document + checklist)  
1. Environment and synthetic data  
2. Part A — Data foundation  
3. Part B — Segmentation  
4. Part C — Ticket triage  
5. Part D — RAG and refund agent  
6. FastAPI + Streamlit  
7. Notebook and documentation  
8. Tests and `run_project.py`  
9. GitHub preparation instructions  

## Testing requirements

Pytest covering data, SQLite, RFM/K-Means, guardrails, RAG, refund simulation, API health.

## Submission requirements

Integrated `main` branch, part branches documented in README, no secrets, no PII in logs/tests.

## Ambiguities / missing input

- No instructor datasets or `generate_data.py` from course — project uses `generate_data.py` in repo root.
- No genuine churn label in synthetic customers — supervised churn metrics are **not** reported; retention uses RFM/at-risk segments only.
