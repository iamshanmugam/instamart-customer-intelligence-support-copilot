"""Numeric EDA summaries only (no chart files per submission guidelines)."""

from __future__ import annotations

import pandas as pd

from src.common.paths import OUTPUTS_EDA, RANDOM_SEED

import numpy as np


def run_eda(datasets: dict[str, pd.DataFrame]) -> None:
    customers = datasets["customers"]
    orders = datasets["orders"]
    tickets = datasets["tickets"]
    OUTPUTS_EDA.mkdir(parents=True, exist_ok=True)

    completed = orders[orders["status"] == "completed"]
    summary = {
        "total_customers": len(customers),
        "total_orders": len(orders),
        "total_tickets": len(tickets),
        "completed_orders": len(completed),
        "avg_order_value_completed": float(completed["order_amount"].mean()) if len(completed) else 0.0,
        "orders_completed_pct": float(len(completed) / len(orders)) if len(orders) else 0.0,
        "tickets_by_category": tickets.get("true_category", pd.Series(dtype=str)).value_counts().to_dict()
        if "true_category" in tickets.columns
        else {},
    }
    pd.Series(summary).to_csv(OUTPUTS_EDA / "eda_summary.csv")
    np.random.seed(RANDOM_SEED)
