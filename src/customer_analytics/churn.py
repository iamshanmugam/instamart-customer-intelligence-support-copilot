from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.common.paths import OUTPUTS_SEGMENTATION


def churn_modeling_report(customers: pd.DataFrame) -> dict:
    """
    No genuine churn label exists in the synthetic customers dataset.
    Do not train supervised classifiers or report Accuracy/Precision/Recall/F1.
    """
    churn_columns = [c for c in customers.columns if "churn" in c.lower()]
    has_label = len(churn_columns) > 0 and customers[churn_columns[0]].notna().any()

    lines = [
        "# Churn Modelling Decision",
        "",
        f"Genuine churn column present: **{has_label}**",
        "",
    ]
    if not has_label:
        lines.extend(
            [
                "Supervised churn modelling was **not** performed.",
                "RFM-based at-risk segments in `retention_list.csv` are behavioural retention indicators,",
                "not probability-of-churn predictions.",
                "",
                "To train Logistic Regression or Random Forest, historical churn labels would be required,",
                "e.g. `churned` within 90 days after last order, with features frozen before that window.",
            ]
        )
    OUTPUTS_SEGMENTATION.mkdir(parents=True, exist_ok=True)
    path = OUTPUTS_SEGMENTATION / "churn_modelling_report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return {"supervised_churn_trained": False, "report_path": str(path)}
