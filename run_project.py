"""
End-to-end pipeline for Instamart Customer Intelligence & Support Co-Pilot.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common.logging_setup import setup_logging
from src.common.paths import OUTPUTS
from src.customer_analytics.churn import churn_modeling_report
from src.customer_analytics.clustering import run_kmeans_pipeline
from src.customer_analytics.rfm import calculate_rfm
from src.data_foundation.clean import clean_all_datasets
from src.data_foundation.eda import run_eda
from src.data_foundation.load import load_raw_datasets, validate_raw_files
from src.database.sqlite_db import create_database, validate_database
from src.rag.assistant import RAGAssistant, build_rag_from_policy, run_sample_rag_queries
from src.agents.refund_agent import RefundAgent
from src.agents.order_lookup import lookup_order
from src.ticket_triage.classifier import classify_tickets_batch

logger = setup_logging()


STAGES = [
    "validate",
    "generate",
    "load",
    "clean",
    "eda",
    "sqlite",
    "rfm",
    "kmeans",
    "churn",
    "triage",
    "rag",
    "refund_samples",
    "all",
]


def stage_validate() -> None:
    missing = validate_raw_files()
    if missing:
        raise FileNotFoundError(f"Missing raw data: {missing}. Run with --stage generate")


def stage_generate() -> None:
    import subprocess

    subprocess.run([sys.executable, str(ROOT / "generate_data.py")], check=True, cwd=ROOT)


def stage_load():
    return load_raw_datasets()


def run_pipeline(stages: list[str] | None = None) -> None:
    stages = stages or ["all"]
    run_all = "all" in stages

    if run_all or "validate" in stages:
        logger.info("Stage: validate datasets")
        try:
            stage_validate()
        except FileNotFoundError:
            logger.info("Raw data missing — generating synthetic data")
            stage_generate()

    raw = None
    if run_all or any(s in stages for s in ("load", "clean", "eda", "sqlite", "rfm", "kmeans", "churn", "triage", "rag")):
        logger.info("Stage: load raw datasets")
        raw = stage_load()

    cleaned = None
    if run_all or any(s in stages for s in ("clean", "eda", "sqlite", "rfm", "kmeans", "churn", "triage", "rag")):
        logger.info("Stage: clean datasets")
        cleaned = clean_all_datasets(raw)

    if run_all or "eda" in stages:
        logger.info("Stage: EDA")
        run_eda(cleaned)

    if run_all or "sqlite" in stages:
        logger.info("Stage: SQLite")
        create_database(cleaned)
        validation = validate_database(cleaned)
        logger.info("SQLite validation: %s", validation)
        (OUTPUTS / "db_validation.txt").write_text(str(validation), encoding="utf-8")

    if run_all or "rfm" in stages:
        logger.info("Stage: RFM")
        rfm = calculate_rfm(cleaned["customers"], cleaned["orders"])
    else:
        rfm = None

    if run_all or "kmeans" in stages:
        if rfm is None:
            rfm = calculate_rfm(cleaned["customers"], cleaned["orders"])
        logger.info("Stage: K-Means & PCA")
        metrics = run_kmeans_pipeline(rfm)
        logger.info("Segmentation: %s", metrics)

    if run_all or "churn" in stages:
        logger.info("Stage: churn decision report")
        churn_modeling_report(cleaned["customers"])

    if run_all or "triage" in stages:
        logger.info("Stage: ticket classification")
        classify_tickets_batch(cleaned["tickets"], limit=100)

    rag = None
    if run_all or "rag" in stages:
        logger.info("Stage: RAG knowledge base")
        rag = build_rag_from_policy(cleaned["policy"])
        run_sample_rag_queries(rag)

    if run_all or "refund_samples" in stages:
        if rag is None:
            rag = RAGAssistant()
            rag.build(cleaned["policy"])
        agent = RefundAgent(rag)
        sample_order = cleaned["orders"].iloc[0]["order_id"]
        lookup_order(str(sample_order))
        agent.run_scenarios()

    logger.info("Pipeline completed successfully.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        action="append",
        choices=STAGES,
        help="Run specific stage(s); default all",
    )
    args = parser.parse_args()
    try:
        run_pipeline(args.stage)
    except Exception as exc:
        logger.exception("Pipeline failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
