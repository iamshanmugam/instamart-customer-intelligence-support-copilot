from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.common.paths import OUTPUTS_EDA, RANDOM_SEED

sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (8, 5)


def _save_fig(name: str) -> None:
    OUTPUTS_EDA.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(OUTPUTS_EDA / name, dpi=120)
    plt.close()


def run_eda(datasets: dict[str, pd.DataFrame]) -> None:
    customers = datasets["customers"]
    orders = datasets["orders"]
    tickets = datasets["tickets"]

    plt.figure()
    customers["city"].value_counts().head(10).plot(kind="bar", title="Customers by City")
    _save_fig("customers_by_city.png")

    if "gender" in customers.columns:
        plt.figure()
        customers["gender"].value_counts().plot(kind="pie", autopct="%1.1f%%", title="Gender")
        _save_fig("customers_gender.png")

    plt.figure()
    orders["order_status"].value_counts().plot(kind="bar", title="Order Status")
    _save_fig("order_status.png")

    plt.figure()
    completed = orders[orders["order_status"] == "Completed"]
    if not completed.empty:
        sns.histplot(completed["order_amount"], bins=30, kde=True)
        plt.title("Completed Order Amount Distribution")
    _save_fig("order_amount_dist.png")

    if "order_date" in orders.columns and pd.api.types.is_datetime64_any_dtype(orders["order_date"]):
        monthly = (
            orders.groupby(orders["order_date"].dt.to_period("M"))
            .size()
            .astype(int)
        )
        plt.figure()
        monthly.plot(kind="line", marker="o", title="Orders Over Time")
        _save_fig("orders_over_time.png")

    plt.figure()
    tickets["category_label"].value_counts().plot(kind="bar", title="Ticket Categories")
    _save_fig("ticket_categories.png")

    plt.figure()
    tickets["priority"].value_counts().plot(kind="bar", title="Ticket Priority")
    _save_fig("ticket_priority.png")

    summary = {
        "total_customers": len(customers),
        "total_orders": len(orders),
        "total_tickets": len(tickets),
        "avg_order_value_completed": float(
            completed["order_amount"].mean() if len(completed) else 0
        ),
    }
    pd.Series(summary).to_csv(OUTPUTS_EDA / "eda_summary.csv")
    import numpy as np

    np.random.seed(RANDOM_SEED)
