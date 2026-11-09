# Instamart Customer Intelligence & Support Co-Pilot

## Overview

End-to-end Python project for Instamart-style customer intelligence and support automation: data cleaning and SQLite storage (Part A), RFM and K-Means segmentation (Part B), guarded ticket classification (Part C), and RAG plus simulated refund workflows (Part D). A mock LLM runs all generative steps without paid API keys.

Pipeline driver: `run_project.py`. SQL examples: `sql/queries.sql`. Tests: `pytest` (13 tests).

## Reproduce

These steps were verified on Windows with Python 3.11+ and a new virtual environment.

```powershell
cd "C:\My AI Projects\Instamart-Customer-Intelligence-Support-Copilot"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
python run_project.py
pytest -q
```

Optional:

```powershell
uvicorn api.main:app --reload
streamlit run frontend/app.py
```

`run_project.py` generates `data/raw/*.csv` via `generate_data.py` when raw files are missing, then writes processed data, `database/Instamart_DB.sqlite`, `outputs/`, and `models/`. Re-running overwrites pipeline outputs deterministically (`RANDOM_SEED=42` in `src/common/paths.py`).

Validate SQL against the database:

```powershell
sqlite3 database/Instamart_DB.sqlite < sql/queries.sql
```

*(Install `sqlite3` CLI if needed, or run queries in DB Browser for SQLite.)*

## Part A

**Scope:** Load, clean, EDA, SQLite.

| Metric | Value | Source |
|--------|------:|--------|
| Raw customer rows | 506 | `data/raw/customers.csv` |
| Cleaned customers | 500 | `outputs/cleaning_report.md` |
| Cleaned orders | 3829 | `outputs/cleaning_report.md` |
| Cleaned tickets | 800 | `outputs/cleaning_report.md` |
| Policy rows (clean) | 5 | `outputs/cleaning_report.md` |
| SQLite `customers` | 500 | `outputs/db_validation.txt` |
| SQLite `orders` | 3829 | `outputs/db_validation.txt` |
| SQLite `tickets` | 800 | `outputs/db_validation.txt` |
| Pandas vs SQLite match | True | `outputs/db_validation.txt` |
| Average completed order value | 791.0233 | `outputs/eda/eda_summary.csv` |

**Artifacts:** `data/processed/*_clean.csv`, `database/Instamart_DB.sqlite`, `outputs/eda/*.png`, `outputs/cleaning_report.md`, `sql/queries.sql`.

## Part B

**Scope:** RFM (completed orders), StandardScaler, K-Means for K=2–8, PCA, segments, retention list. No supervised churn model (no genuine churn label).

| Metric | Value | Source |
|--------|------:|--------|
| RFM reference date | 2025-10-31 | `outputs/segmentation/rfm_reference_date.txt` |
| Customers with ≥1 completed order (segmented) | 484 | `outputs/segmentation/customer_segments.csv` |
| Customers with no completed orders | 16 | `outputs/segmentation/inactive_customers.csv` |
| Retention list rows | 107 | `outputs/segmentation/retention_list.csv` |
| Highest silhouette K (evaluation) | 2 (score 0.4676) | `outputs/segmentation/kmeans_evaluation.csv` |
| Final K-Means K (applied model) | 3 | `models/kmeans_model.joblib` / pipeline logic |
| K=2 inertia / silhouette | 664.1245 / 0.4676 | `outputs/segmentation/kmeans_evaluation.csv` |
| K=3 inertia / silhouette | 412.4266 / 0.4535 | `outputs/segmentation/kmeans_evaluation.csv` |
| K=8 inertia / silhouette | 173.0573 / 0.3406 | `outputs/segmentation/kmeans_evaluation.csv` |
| PCA PC1 variance ratio | 0.7664 | `outputs/segmentation/pca_variance.csv` |
| PCA PC2 variance ratio | 0.2007 | `outputs/segmentation/pca_variance.csv` |
| PCA cumulative (2 components) | 0.9671 | `outputs/segmentation/pca_variance.csv` |
| Cluster 0 / 1 / 2 sizes | 196 / 62 / 226 | `outputs/segmentation/customer_segments.csv` |

**Artifacts:** `outputs/segmentation/rfm_scores.csv`, `kmeans_evaluation.csv`, `customer_segments.csv`, `retention_list.csv`, `elbow_chart.png`, `silhouette_chart.png`, `pca_clusters.png`, `churn_modelling_report.md`.

## Part C

**Scope:** Ticket categories, priority, routing, guardrails, PII masking, zero/few-shot classification via `mock_llm.py`, batch output via pipeline.

| Metric | Value | Source |
|--------|------:|--------|
| Tickets classified (batch limit) | 100 | `outputs/ticket_triage/classified_tickets.csv` |
| Successful classifications | 100 | same |
| Rejected (guardrails) | 0 | same |
| Max ticket characters (config default) | 4000 | `.env.example` |

**Artifacts:** `src/ticket_triage/`, `triage.py`, `outputs/ticket_triage/classified_tickets.csv`.

## Part D

**Scope:** Policy knowledge base, TF-IDF retrieval, RAG Q&A, SQLite order lookup, simulated refund agent.

| Metric | Value | Source |
|--------|------:|--------|
| Policy documents in knowledge base | 5 | `data/raw/policy_evaluation.csv` |
| Sample RAG queries in pipeline output | 3 | `outputs/rag/sample_rag_results.json` |
| Automated tests passing | 13 | `pytest -q` (last run) |

**Artifacts:** `data/knowledge_base/policies.txt`, `data/knowledge_base/vector_index.json`, `outputs/rag/sample_rag_results.json`, `outputs/rag/simulated_refunds.jsonl`, `src/rag/`, `src/agents/`.

## Limitations and Next Steps

- **Instructor files:** Two original supplied files are required unmodified; they are not present in `instructor-materials/` yet—add them before submission (see that folder’s README).
- **Data:** Raw CSVs are synthetic from `generate_data.py` unless official instructor datasets are added.
- **Churn:** No labelled churn target; retention uses RFM/at-risk segments only (`outputs/segmentation/churn_modelling_report.md`).
- **LLM:** Default `LLM_PROVIDER=mock`; configure a real provider in `.env` when keys are available.
- **Refunds:** Simulation only; fraud cases escalate to a human agent.
- **GitHub:** Use one public repository with default branch **`main`** (rename locally from `master` if needed). Do not commit `.venv/`, `.env`, or `.pytest_cache/`.
- **Extra docs:** `LEARNING_GUIDE.md`, `docs/`, and `notebooks/` support learning but are not substitutes for this README’s submission sections.
