"""
Reproducible synthetic datasets for Instamart Co-Pilot.
No instructor data was available at project discovery — all raw CSVs are locally generated.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from src.common.paths import DATA_RAW, RANDOM_SEED

np.random.seed(RANDOM_SEED)

CITIES = ["Bengaluru", "Mumbai", "Delhi", "Chennai", "Hyderabad", "Pune", "Kolkata"]
GENDERS = ["Male", "Female", "Unknown"]
ORDER_STATUSES = ["Completed", "Cancelled", "Refunded", "Pending"]
TICKET_CATEGORIES = [
    "Refund",
    "Delivery Delay",
    "Payment",
    "Fraud",
    "Product Quality",
    "App Issue",
    "Other",
]


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def generate_customers(n: int = 500) -> pd.DataFrame:
    ids = [f"CUST{i:05d}" for i in range(1, n + 1)]
    reg_start = datetime(2023, 1, 1)
    rows = []
    for i, cid in enumerate(ids):
        reg = reg_start + timedelta(days=int(np.random.randint(0, 600)))
        gender = np.random.choice(GENDERS, p=[0.48, 0.48, 0.04])
        city = np.random.choice(CITIES)
        # Inject duplicates and missing for cleaning demo
        if i % 97 == 0:
            rows.append(rows[-1].copy()) if rows else None
        email = f"user{i}@example.com"
        phone = f"+91{np.random.randint(700000000, 999999999)}"
        rows.append(
            {
                "customer_id": cid,
                "name": f"Customer {i}",
                "email": email if i % 50 != 0 else np.nan,
                "phone": phone,
                "gender": gender if i % 80 != 0 else "M",
                "city": city if i % 60 != 0 else "bangalore",
                "registration_date": reg.strftime("%Y-%m-%d"),
            }
        )
    df = pd.DataFrame(rows)
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
    return df


def generate_orders(customers: pd.DataFrame, n_per_customer: tuple = (1, 15)) -> pd.DataFrame:
    rows = []
    order_num = 1
    base = datetime(2024, 1, 1)
    for _, cust in customers.drop_duplicates("customer_id").iterrows():
        k = np.random.randint(n_per_customer[0], n_per_customer[1] + 1)
        for _ in range(k):
            days = np.random.randint(0, 640)
            dt = base + timedelta(days=days)
            status = np.random.choice(
                ORDER_STATUSES, p=[0.72, 0.12, 0.08, 0.08]
            )
            amount = round(float(np.random.lognormal(6.5, 0.6)), 2)
            if amount > 5000:
                amount = round(amount * 0.3, 2)
            rows.append(
                {
                    "order_id": f"ORD{order_num:06d}",
                    "customer_id": cust["customer_id"],
                    "order_date": dt.strftime("%Y-%m-%d"),
                    "order_status": status,
                    "order_amount": amount if order_num % 200 != 0 else -10,
                    "city": cust["city"] if isinstance(cust["city"], str) else "Bengaluru",
                }
            )
            order_num += 1
    return pd.DataFrame(rows)


TICKET_TEMPLATES = {
    "Refund": "I want a refund for order {oid}. Item was damaged.",
    "Delivery Delay": "Order {oid} is very late. Please help.",
    "Payment": "Payment failed but amount debited for order {oid}.",
    "Fraud": "Suspicious activity on my account related to order {oid}.",
    "Product Quality": "Poor quality products in order {oid}.",
    "App Issue": "App crashes when I track order {oid}.",
    "Other": "General inquiry about order {oid}.",
}


def generate_tickets(orders: pd.DataFrame, n: int = 800) -> pd.DataFrame:
    sample_orders = orders.sample(n=min(n, len(orders)), replace=True, random_state=RANDOM_SEED)
    priorities = ["Critical", "High", "Medium", "Low"]
    statuses = ["Open", "In Progress", "Resolved", "Closed"]
    rows = []
    for i, (_, ord_row) in enumerate(sample_orders.iterrows()):
        cat = ord_row.get("issue_category")
        if cat is None or (isinstance(cat, float) and np.isnan(cat)):
            cat = np.random.choice(TICKET_CATEGORIES)
        else:
            cat = TICKET_CATEGORIES[i % len(TICKET_CATEGORIES)]
        if i < len(TICKET_CATEGORIES):
            cat = TICKET_CATEGORIES[i % len(TICKET_CATEGORIES)]
        oid = ord_row["order_id"]
        text = TICKET_TEMPLATES.get(cat, TICKET_TEMPLATES["Other"]).format(oid=oid)
        text += f" Contact me at user{i}@example.com or +9198765{i:04d}."
        rows.append(
            {
                "ticket_id": f"TKT{i+1:05d}",
                "customer_id": ord_row["customer_id"],
                "order_id": oid,
                "created_at": ord_row["order_date"],
                "category_label": cat,
                "priority": np.random.choice(priorities),
                "status": np.random.choice(statuses),
                "ticket_text": text,
            }
        )
    return pd.DataFrame(rows)


def generate_policy_evaluation() -> pd.DataFrame:
    policies = [
        {
            "policy_id": "POL-REF-001",
            "policy_title": "Refund within 24 hours of delivery",
            "policy_text": (
                "Customers may request a full refund within 24 hours of confirmed delivery "
                "if items are damaged, expired, or missing. Proof photo may be required. "
                "Refunds are not automatic for orders marked Delivered more than 48 hours ago."
            ),
            "category": "Refund",
        },
        {
            "policy_id": "POL-REF-002",
            "policy_title": "Partial refund for quality issues",
            "policy_text": (
                "Product quality complaints may qualify for partial refund up to 50% when "
                "the item is usable but below quality standards. Fraud or repeated abuse "
                "of refunds leads to manual review."
            ),
            "category": "Refund",
        },
        {
            "policy_id": "POL-DEL-001",
            "policy_title": "Delivery delay compensation",
            "policy_text": (
                "If delivery exceeds promised time by more than 45 minutes, customer may "
                "receive a voucher. Escalate to operations if delay exceeds 2 hours."
            ),
            "category": "Delivery Delay",
        },
        {
            "policy_id": "POL-PAY-001",
            "policy_title": "Payment failure and double debit",
            "policy_text": (
                "Failed payments may still show pending debit for 3-5 bank working days. "
                "Escalate to payment team if debit persists beyond 7 days with transaction ID."
            ),
            "category": "Payment",
        },
        {
            "policy_id": "POL-FRD-001",
            "policy_title": "Fraud escalation",
            "policy_text": (
                "All fraud allegations require human review. Do not auto-approve refunds "
                "for fraud tickets. Collect order ID and verify account activity."
            ),
            "category": "Fraud",
        },
    ]
    eval_rows = []
    for p in policies:
        eval_rows.append(
            {
                "policy_id": p["policy_id"],
                "policy_title": p["policy_title"],
                "policy_text": p["policy_text"],
                "category": p["category"],
                "sample_question": f"What is the rule for {p['category'].lower()}?",
                "expected_answer_hint": p["policy_text"][:120] + "...",
            }
        )
    return pd.DataFrame(eval_rows)


def main(force: bool = False) -> None:
    _ensure_dir(DATA_RAW)
    paths = {
        "customers.csv": generate_customers,
        "orders.csv": None,
        "support_tickets.csv": None,
        "policy_evaluation.csv": generate_policy_evaluation,
    }
    cust_path = DATA_RAW / "customers.csv"
    if force or not cust_path.exists():
        customers = generate_customers()
        customers.to_csv(cust_path, index=False)
        print(f"Wrote {cust_path} ({len(customers)} rows)")
    else:
        customers = pd.read_csv(cust_path)

    ord_path = DATA_RAW / "orders.csv"
    if force or not ord_path.exists():
        orders = generate_orders(customers)
        orders.to_csv(ord_path, index=False)
        print(f"Wrote {ord_path} ({len(orders)} rows)")
    else:
        orders = pd.read_csv(ord_path)

    tix_path = DATA_RAW / "support_tickets.csv"
    if force or not tix_path.exists():
        tickets = generate_tickets(orders)
        tickets.to_csv(tix_path, index=False)
        print(f"Wrote {tix_path} ({len(tickets)} rows)")

    pol_path = DATA_RAW / "policy_evaluation.csv"
    if force or not pol_path.exists():
        policy = generate_policy_evaluation()
        policy.to_csv(pol_path, index=False)
        print(f"Wrote {pol_path} ({len(policy)} rows)")

    print("Synthetic data generation complete (documented as local sample data).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Regenerate all CSVs")
    main(force=parser.parse_args().force)
