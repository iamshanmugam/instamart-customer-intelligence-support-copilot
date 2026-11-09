from __future__ import annotations

from datetime import date

import pandas as pd

from src.common.config import get_rfm_reference_date
from src.common.paths import OUTPUTS_SEGMENTATION


def calculate_rfm(
    customers: pd.DataFrame,
    orders: pd.DataFrame,
    reference_date: date | None = None,
) -> pd.DataFrame:
    reference_date = reference_date or get_rfm_reference_date()
    ref = pd.Timestamp(reference_date)

    status_col = "status" if "status" in orders.columns else "order_status"
    completed = orders[orders[status_col].astype(str).str.lower() == "completed"].copy()
    date_col = "order_ts" if "order_ts" in completed.columns else "order_date"
    completed[date_col] = pd.to_datetime(completed[date_col], errors="coerce")

    agg = (
        completed.groupby("customer_id")
        .agg(
            last_order=(date_col, "max"),
            frequency=("order_id", "nunique"),
            monetary=("order_amount", "sum"),
        )
        .reset_index()
    )
    agg["recency_days"] = (ref - agg["last_order"]).dt.days
    all_customers = customers[["customer_id"]].drop_duplicates()
    rfm = all_customers.merge(agg, on="customer_id", how="left")
    rfm["recency_days"] = rfm["recency_days"].fillna(9999)
    rfm["frequency"] = rfm["frequency"].fillna(0).astype(int)
    rfm["monetary"] = rfm["monetary"].fillna(0.0)

    OUTPUTS_SEGMENTATION.mkdir(parents=True, exist_ok=True)
    meta = f"RFM reference date: {reference_date.isoformat()}\n"
    (OUTPUTS_SEGMENTATION / "rfm_reference_date.txt").write_text(meta, encoding="utf-8")
    rfm.to_csv(OUTPUTS_SEGMENTATION / "rfm_scores.csv", index=False)
    return rfm
