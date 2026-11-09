# Instamart Customer Intelligence & Support Co-Pilot

## Overview

Capstone project on **instructor-supplied** synthetic Instamart data (`generate_data.py`, `mock_llm.py` unchanged). Part A cleans data and loads SQLite; Part B builds RFM and K-Means segments; Part C classifies support tickets via `mock_llm.chat` with guardrails; Part D runs policy Q&A and a simulated refund agent. All LLM steps are offline. Numeric results are reported here as text only (no chart files in the repository).

## Reproduce

Evaluated on Windows with Python 3.11+.

```powershell
git clone https://github.com/iamshanmugam/instamart-customer-intelligence-support-copilot.git
cd instamart-customer-intelligence-support-copilot
git checkout main
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python generate_data.py
python run_project.py
pytest -q
```

`python generate_data.py` writes `data/raw/*.csv` and `data/policies/*.txt`. `python run_project.py` writes `data/processed/`, `database/Instamart_DB.sqlite`, `outputs/`, and `models/`. Random seed **42** is set in `src/common/paths.py` for student code; instructor scripts use `random.Random(42)`.

Optional SQL check (if `sqlite3` CLI is installed):  
`sqlite3 database/Instamart_DB.sqlite < sql/queries.sql`

## Part A

**Scope:** Load, clean, numeric EDA summary, SQLite.

| Metric | Value | Source |
|--------|------:|--------|
| Raw customers | 1200 | `data/raw/customers.csv` |
| Raw orders (rows) | 13084 | `data/raw/orders.csv` |
| Raw tickets | 164 | `data/raw/tickets.csv` |
| Products | 40 | `data/raw/products.csv` |
| Policy eval questions | 14 | `data/raw/policy_eval.csv` |
| Cleaned customers | 1200 | `outputs/cleaning_report.md` |
| Cleaned orders | 12309 | `outputs/cleaning_report.md` |
| Cleaned tickets | 160 | `outputs/cleaning_report.md` |
| SQLite customers | 1200 | `outputs/db_validation.txt` |
| SQLite orders | 12309 | `outputs/db_validation.txt` |
| SQLite tickets | 160 | `outputs/db_validation.txt` |
| SQLite products | 40 | `outputs/db_validation.txt` |
| Pandas vs SQLite match | True | `outputs/db_validation.txt` |
| Completed orders (cleaned) | 11110 | `outputs/eda/eda_summary.csv` |
| Share completed | 0.9026 | `outputs/eda/eda_summary.csv` |
| Avg completed order value (INR) | 268.5576 | `outputs/eda/eda_summary.csv` |

**Artifacts (text/code):** `data/processed/*_clean.csv`, `database/Instamart_DB.sqlite`, `outputs/cleaning_report.md`, `outputs/eda/eda_summary.csv`, `sql/queries.sql`.

## Part B

**Scope:** RFM (completed orders), `StandardScaler`, K-Means for K=2–8, PCA variance summary, segments, retention list. No supervised churn model.

| Metric | Value | Source |
|--------|------:|--------|
| RFM reference date | 2025-09-30 | `outputs/segmentation/rfm_reference_date.txt` |
| Customers with ≥1 completed order | 1175 | `outputs/segmentation/customer_segments.csv` |
| Customers with no completed orders | 25 | `outputs/segmentation/inactive_customers.csv` |
| Retention list rows | 270 | `outputs/segmentation/retention_list.csv` |
| Best silhouette K | 4 (0.5259) | `outputs/segmentation/kmeans_evaluation.csv` |
| Applied K-Means K | 4 | `models/kmeans_model.joblib` |
| K=2 inertia / silhouette | 1818.0189 / 0.4662 | `outputs/segmentation/kmeans_evaluation.csv` |
| K=4 inertia / silhouette | 742.1261 / 0.5259 | `outputs/segmentation/kmeans_evaluation.csv` |
| K=8 inertia / silhouette | 366.4247 / 0.4017 | `outputs/segmentation/kmeans_evaluation.csv` |
| PCA PC1 variance | 0.6349 | `outputs/segmentation/pca_variance.csv` |
| PCA PC2 variance | 0.2176 | `outputs/segmentation/pca_variance.csv` |
| PCA cumulative (2D) | 0.8525 | `outputs/segmentation/pca_variance.csv` |
| Cluster sizes 0–3 | 436 / 183 / 137 / 419 | `outputs/segmentation/customer_segments.csv` |

**Artifacts:** `outputs/segmentation/rfm_scores.csv`, `kmeans_evaluation.csv`, `customer_segments.csv`, `retention_list.csv`, `pca_variance.csv`, `churn_modelling_report.md`, `models/rfm_scaler.joblib`, `models/kmeans_model.joblib`.

## Part C

**Scope:** Ticket categories (`billing`, `delivery`, `technical`, `fraud`), guardrails, PII masking, `mock_llm` zero/few-shot classification.

| Metric | Value | Source |
|--------|------:|--------|
| Tickets classified (batch) | 100 | `outputs/ticket_triage/classified_tickets.csv` |
| Successful classifications | 100 | same |
| Guardrail rejections | 0 | same |
| Max ticket length (config) | 4000 chars | `.env.example` |

**Artifacts:** `src/ticket_triage/`, `triage.py`, `outputs/ticket_triage/classified_tickets.csv`.

## Part D

**Scope:** Policy texts in `data/policies/`, RAG-style retrieval + `POLICY ASSISTANT` in `mock_llm`, agent scenarios CSV.

| Metric | Value | Source |
|--------|------:|--------|
| Policy text files | 5 | `data/policies/` |
| Policy eval rows | 14 | `data/raw/policy_eval.csv` |
| Sample RAG questions run | 3 | `outputs/rag/sample_rag_results.json` |
| Agent scenarios processed | 7 | `outputs/rag/agent_scenario_results.csv` |
| Automated tests | 13 passed | `pytest -q` |

**Artifacts:** `data/knowledge_base/vector_index.json`, `outputs/rag/sample_rag_results.json`, `outputs/rag/agent_scenario_results.csv`, `outputs/rag/simulated_refunds.jsonl`, `src/rag/`, `src/agents/`.

## Limitations and Next Steps

- **Supplied files:** `generate_data.py` and `mock_llm.py` at repo root match `instructor-materials/` copies (unmodified). Do not edit them.
- **Submission format:** No images or PDFs in the repo; findings are numeric in this README and CSV/JSON under `outputs/`.
- **Churn:** No churn label in supplied data; see `outputs/segmentation/churn_modelling_report.md`.
- **Libraries:** Core grading uses pandas, numpy, scikit-learn, joblib; optional API/UI packages in `requirements.txt` are not required for Reproduce.
- **GitHub:** Submit only `https://github.com/iamshanmugam/instamart-customer-intelligence-support-copilot/tree/main`.
