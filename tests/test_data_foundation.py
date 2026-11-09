from pathlib import Path

import pandas as pd
import pytest

from src.data_foundation.load import DataLoadError, load_csv, validate_raw_files
from src.data_foundation.clean import clean_customers, clean_orders


def test_missing_file_raises(tmp_path):
    with pytest.raises(DataLoadError):
        load_csv(tmp_path / "nope.csv")


def test_clean_customers_dedupes():
    df = pd.DataFrame(
        [
            {"customer_id": "C1", "city": "bangalore", "gender": "M", "registration_date": "2024-01-01", "email": None, "phone": "1", "name": "A"},
            {"customer_id": "C1", "city": "mumbai", "gender": "F", "registration_date": "2024-01-02", "email": "a@b.com", "phone": "2", "name": "B"},
        ]
    )
    out = clean_customers(df)
    assert len(out) == 1
    assert out.iloc[0]["city"] == "Bengaluru"
    assert out.iloc[0]["gender"] == "Male"


def test_clean_orders_drops_invalid_customers():
    orders = pd.DataFrame(
        [
            {
                "order_id": "ORD-100001",
                "customer_id": "CX",
                "order_ts": "2024-01-01 12:00:00",
                "status": "completed",
                "order_amount": 100,
                "delivery_minutes": 20,
            },
        ]
    )
    out = clean_orders(orders, {"C1"})
    assert len(out) == 0
