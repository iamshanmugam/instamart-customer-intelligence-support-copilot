from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.common.paths import DATA_RAW


REQUIRED_FILES = [
    "customers.csv",
    "orders.csv",
    "support_tickets.csv",
    "policy_evaluation.csv",
]


class DataLoadError(FileNotFoundError):
    pass


def validate_raw_files(data_dir: Path | None = None) -> list[str]:
    data_dir = data_dir or DATA_RAW
    missing = [f for f in REQUIRED_FILES if not (data_dir / f).exists()]
    return missing


def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise DataLoadError(f"Missing dataset: {path}")
    return pd.read_csv(path)


def load_raw_datasets(data_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    data_dir = data_dir or DATA_RAW
    missing = validate_raw_files(data_dir)
    if missing:
        raise DataLoadError(f"Missing files in {data_dir}: {missing}")
    return {
        "customers": load_csv(data_dir / "customers.csv"),
        "orders": load_csv(data_dir / "orders.csv"),
        "tickets": load_csv(data_dir / "support_tickets.csv"),
        "policy": load_csv(data_dir / "policy_evaluation.csv"),
    }


def inspect_dataset(df: pd.DataFrame, name: str) -> dict[str, Any]:
    return {
        "name": name,
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "missing_counts": df.isna().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
    }
