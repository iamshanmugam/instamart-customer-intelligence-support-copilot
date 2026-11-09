# Required repository contents (checklist)

Use this alongside the course handout. After `python generate_data.py` and `python run_project.py`, these paths should exist on branch **main**.

## Supplied (unmodified)

- `generate_data.py`
- `mock_llm.py`
- `instructor-materials/generate_data.py` (identical copy)
- `instructor-materials/mock_llm.py` (identical copy)

## Project config

- `requirements.txt`
- `.gitignore`
- `sql/queries.sql`
- `README.md` (sections: Overview, Reproduce, Part A–D, Limitations and Next Steps)

## Source (Parts A–D)

- `src/data_foundation/`, `src/database/`, `src/customer_analytics/`
- `src/ticket_triage/`, `src/rag/`, `src/agents/`
- `run_project.py`, `triage.py`, `tests/`

## Generated / committed outputs (text only — no PNG/PDF)

| Area | Paths |
|------|--------|
| Raw (from supplied generator) | `data/raw/customers.csv`, `orders.csv`, `tickets.csv`, `policy_eval.csv`, `products.csv`, `agent_scenarios.csv` |
| Policies (from supplied generator) | `data/policies/*.txt` |
| Processed | `data/processed/*_clean.csv` |
| Database | `database/Instamart_DB.sqlite` |
| Part A reports | `outputs/cleaning_report.md`, `outputs/db_validation.txt`, `outputs/eda/eda_summary.csv` |
| Part B | `outputs/segmentation/*.csv`, `outputs/segmentation/churn_modelling_report.md`, `models/*.joblib` |
| Part C | `outputs/ticket_triage/classified_tickets.csv` |
| Part D | `outputs/rag/*.json`, `outputs/rag/*.csv`, `outputs/rag/simulated_refunds.jsonl`, `data/knowledge_base/vector_index.json` |

## Must not be in the repository

- Images (`*.png`, `*.jpg`, screenshots)
- PDFs, decks, video, audio
- `.venv/`, `.env`, secrets
