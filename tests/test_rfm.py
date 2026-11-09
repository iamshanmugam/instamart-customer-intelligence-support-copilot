import pandas as pd

from src.customer_analytics.rfm import calculate_rfm
from datetime import date


def test_rfm_no_completed_orders():
    customers = pd.DataFrame({"customer_id": ["C1", "C2"]})
    orders = pd.DataFrame(
        [
            {"customer_id": "C1", "order_id": "O1", "order_date": "2024-06-01", "order_status": "Cancelled", "order_amount": 50},
        ]
    )
    rfm = calculate_rfm(customers, orders, reference_date=date(2024, 12, 1))
    assert rfm.loc[rfm.customer_id == "C1", "frequency"].iloc[0] == 0
    assert rfm.loc[rfm.customer_id == "C2", "recency_days"].iloc[0] == 9999
