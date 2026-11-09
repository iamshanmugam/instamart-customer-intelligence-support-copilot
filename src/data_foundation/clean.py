from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.common.paths import DATA_PROCESSED, OUTPUTS, RANDOM_SEED

CITY_MAP = {
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",
    "mumbai": "Mumbai",
    "delhi": "Delhi",
    "chennai": "Chennai",
    "hyderabad": "Hyderabad",
    "pune": "Pune",
    "kolkata": "Kolkata",
}

GENDER_MAP = {"M": "Male", "F": "Female", "male": "Male", "female": "Female"}


def _standardize_city(series: pd.Series) -> pd.Series:
    def fix(val):
        if pd.isna(val):
            return "Unknown"
        s = str(val).strip()
        return CITY_MAP.get(s.lower(), s.title())

    return series.apply(fix)


def _standardize_gender(series: pd.Series) -> pd.Series:
    def fix(val):
        if pd.isna(val):
            return "Unknown"
        s = str(val).strip()
        return GENDER_MAP.get(s, s if s in ("Male", "Female", "Unknown") else "Unknown")

    return series.apply(fix)


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.drop_duplicates(subset=["customer_id"], keep="first").copy()
    out["city"] = _standardize_city(out["city"])
    out["gender"] = _standardize_gender(out["gender"])
    out["registration_date"] = pd.to_datetime(out["registration_date"], errors="coerce")
    out["email"] = out["email"].fillna("unknown@placeholder.local")
    out["phone"] = out["phone"].astype(str)
    return out


def clean_orders(df: pd.DataFrame, valid_customer_ids: set) -> pd.DataFrame:
    out = df.drop_duplicates(subset=["order_id"], keep="first").copy()
    out["order_date"] = pd.to_datetime(out["order_date"], errors="coerce")
    out["city"] = _standardize_city(out["city"])
    out = out[out["customer_id"].isin(valid_customer_ids)]
    out.loc[out["order_amount"] <= 0, "order_amount"] = np.nan
    median_amt = out["order_amount"].median()
    out["order_amount"] = out["order_amount"].fillna(median_amt if pd.notna(median_amt) else 0)
    out["order_status"] = out["order_status"].astype(str).str.strip().str.title()
    status_map = {
        "Completed": "Completed",
        "Cancelled": "Cancelled",
        "Refunded": "Refunded",
        "Pending": "Pending",
    }
    out["order_status"] = out["order_status"].map(lambda x: status_map.get(x, x))
    return out


def clean_tickets(df: pd.DataFrame, valid_customer_ids: set) -> pd.DataFrame:
    out = df.drop_duplicates(subset=["ticket_id"], keep="first").copy()
    out["created_at"] = pd.to_datetime(out["created_at"], errors="coerce")
    out = out[out["customer_id"].isin(valid_customer_ids)]
    out["ticket_text"] = out["ticket_text"].astype(str).str.strip()
    out = out[out["ticket_text"].str.len() > 0]
    return out


def clean_policy(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(subset=["policy_id"], keep="first").copy()


def clean_all_datasets(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    customers = clean_customers(datasets["customers"])
    cust_ids = set(customers["customer_id"])
    orders = clean_orders(datasets["orders"], cust_ids)
    tickets = clean_tickets(datasets["tickets"], cust_ids)
    policy = clean_policy(datasets["policy"])

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    customers.to_csv(DATA_PROCESSED / "customers_clean.csv", index=False)
    orders.to_csv(DATA_PROCESSED / "orders_clean.csv", index=False)
    tickets.to_csv(DATA_PROCESSED / "tickets_clean.csv", index=False)
    policy.to_csv(DATA_PROCESSED / "policy_evaluation_clean.csv", index=False)

    report_lines = [
        "# Data Cleaning Report",
        "",
        f"- Customers: {len(datasets['customers'])} -> {len(customers)} (dedupe by customer_id)",
        f"- Orders: {len(datasets['orders'])} -> {len(orders)} (invalid customers/amounts handled)",
        f"- Tickets: {len(datasets['tickets'])} -> {len(tickets)}",
        f"- Policy rows: {len(policy)}",
        "",
        "## Decisions",
        "- City/gender standardized; placeholder email for missing emails (not dropped).",
        "- Negative/zero order amounts imputed with median.",
        "- Orders/tickets without valid customer_id removed.",
    ]
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    (OUTPUTS / "cleaning_report.md").write_text("\n".join(report_lines), encoding="utf-8")
    np.random.seed(RANDOM_SEED)
    return {
        "customers": customers,
        "orders": orders,
        "tickets": tickets,
        "policy": policy,
    }
