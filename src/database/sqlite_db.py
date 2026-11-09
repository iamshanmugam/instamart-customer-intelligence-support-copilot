from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.common.paths import DATABASE_DIR, DATABASE_PATH


def create_database(datasets: dict[str, pd.DataFrame], db_path: Path | None = None) -> Path:
    db_path = db_path or DATABASE_PATH
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    try:
        customers = datasets["customers"].copy()
        orders = datasets["orders"].copy()
        tickets = datasets["tickets"].copy()
        if "registration_date" in customers.columns:
            customers["registration_date"] = customers["registration_date"].astype(str)
        if "order_date" in orders.columns:
            orders["order_date"] = orders["order_date"].astype(str)
        if "created_at" in tickets.columns:
            tickets["created_at"] = tickets["created_at"].astype(str)

        customers.to_sql("customers", conn, index=False, if_exists="replace")
        orders.to_sql("orders", conn, index=False, if_exists="replace")
        tickets.to_sql("tickets", conn, index=False, if_exists="replace")

        conn.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
            CREATE INDEX IF NOT EXISTS idx_tickets_customer ON tickets(customer_id);
            """
        )
        conn.commit()
    finally:
        conn.close()
    return db_path


def validate_database(
    datasets: dict[str, pd.DataFrame], db_path: Path | None = None
) -> dict[str, int | bool]:
    db_path = db_path or DATABASE_PATH
    conn = sqlite3.connect(db_path)
    try:
        counts = {}
        for table in ("customers", "orders", "tickets"):
            counts[table] = int(
                pd.read_sql_query(f"SELECT COUNT(*) as c FROM {table}", conn)["c"][0]
            )
        expected = {
            "customers": len(datasets["customers"]),
            "orders": len(datasets["orders"]),
            "tickets": len(datasets["tickets"]),
        }
        match = all(counts[k] == expected[k] for k in expected)
        return {**counts, "counts_match_pandas": match}
    finally:
        conn.close()
