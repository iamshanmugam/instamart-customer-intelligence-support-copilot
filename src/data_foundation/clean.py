from __future__ import annotations

import numpy as np
import pandas as pd

from src.common.paths import DATA_PROCESSED, OUTPUTS, RANDOM_SEED

CITY_MAP = {
    "bengaluru": "Bengaluru",
    "bangalore": "Bengaluru",
    "mumbai": "Mumbai",
    "delhi": "Delhi",
    "chennai": "Chennai",
    "hyderabad": "Hyderabad",
    "pune": "Pune",
}


def _standardize_city(series: pd.Series) -> pd.Series:
    def fix(val):
        if pd.isna(val):
            return "Unknown"
        s = str(val).strip()
        return CITY_MAP.get(s.lower(), s.title())

    return series.apply(fix)


def _standardize_gender(series: pd.Series) -> pd.Series:
    def fix(val):
        if pd.isna(val) or str(val).strip() == "":
            return "Unknown"
        s = str(val).strip().lower()
        if s in ("m", "male"):
            return "Male"
        if s in ("f", "female"):
            return "Female"
        return "Unknown"

    return series.apply(fix)


def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.drop_duplicates(subset=["customer_id"], keep="first").copy()
    out["city"] = _standardize_city(out["city"])
    if "gender" in out.columns:
        out["gender"] = _standardize_gender(out["gender"])
    if "signup_date" in out.columns:
        out["signup_date"] = pd.to_datetime(out["signup_date"], errors="coerce")
    if "age" in out.columns:
        out.loc[out["age"].apply(lambda x: pd.isna(x) or str(x).strip() == ""), "age"] = np.nan
        out["age"] = pd.to_numeric(out["age"], errors="coerce")
        out.loc[(out["age"] < 13) | (out["age"] > 100), "age"] = np.nan
    return out


def clean_orders(df: pd.DataFrame, valid_customer_ids: set) -> pd.DataFrame:
    out = df.copy()
    out["order_ts"] = pd.to_datetime(out["order_ts"], errors="coerce")
    out["order_amount"] = pd.to_numeric(out["order_amount"], errors="coerce")
    out["delivery_minutes"] = pd.to_numeric(out["delivery_minutes"], errors="coerce")
    out.loc[out["delivery_minutes"] < 0, "delivery_minutes"] = np.nan
    out = out[out["customer_id"].isin(valid_customer_ids)]
    out["status"] = out["status"].astype(str).str.strip().str.lower()
    out = out.sort_values(["order_id", "order_ts"])
    out = out.drop_duplicates(subset=["order_id"], keep="last")
    median_amt = out["order_amount"].median()
    out["order_amount"] = out["order_amount"].fillna(median_amt if pd.notna(median_amt) else 0)
    return out


def clean_tickets(df: pd.DataFrame, valid_customer_ids: set) -> pd.DataFrame:
    out = df.drop_duplicates(subset=["ticket_id"], keep="first").copy()
    text_col = "text" if "text" in out.columns else "ticket_text"
    out = out[out["customer_id"].isin(valid_customer_ids)]
    out[text_col] = out[text_col].astype(str).str.strip()
    out = out[out[text_col].str.len() > 0]
    out = out.rename(columns={text_col: "ticket_text"})
    return out


def clean_policy(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates().copy()


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(subset=["product_id"], keep="first").copy()


def clean_all_datasets(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    customers = clean_customers(datasets["customers"])
    cust_ids = set(customers["customer_id"])
    orders = clean_orders(datasets["orders"], cust_ids)
    tickets = clean_tickets(datasets["tickets"], cust_ids)
    policy = clean_policy(datasets["policy"])
    products = clean_products(datasets["products"])

    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    customers.to_csv(DATA_PROCESSED / "customers_clean.csv", index=False)
    orders.to_csv(DATA_PROCESSED / "orders_clean.csv", index=False)
    tickets.to_csv(DATA_PROCESSED / "tickets_clean.csv", index=False)
    policy.to_csv(DATA_PROCESSED / "policy_eval_clean.csv", index=False)
    products.to_csv(DATA_PROCESSED / "products_clean.csv", index=False)

    report_lines = [
        "# Data Cleaning Report",
        "",
        f"- Customers: {len(datasets['customers'])} -> {len(customers)}",
        f"- Orders: {len(datasets['orders'])} -> {len(orders)}",
        f"- Tickets: {len(datasets['tickets'])} -> {len(tickets)}",
        f"- Policy eval rows: {len(policy)}",
        f"- Products: {len(products)}",
        "",
        "## Decisions",
        "- Cities normalised; invalid ages and negative delivery minutes set to missing.",
        "- Duplicate order_id rows kept at latest order_ts.",
        "- Empty ticket text removed.",
    ]
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    (OUTPUTS / "cleaning_report.md").write_text("\n".join(report_lines), encoding="utf-8")
    np.random.seed(RANDOM_SEED)
    return {
        "customers": customers,
        "orders": orders,
        "tickets": tickets,
        "policy": policy,
        "products": products,
    }
