import os
from datetime import date

from dotenv import load_dotenv

from .paths import PROJECT_ROOT, RANDOM_SEED

load_dotenv(PROJECT_ROOT / ".env")


def get_rfm_reference_date() -> date:
    raw = os.getenv("RFM_REFERENCE_DATE", "2025-09-30")
    y, m, d = map(int, raw.split("-"))
    return date(y, m, d)


MAX_TICKET_CHARS = int(os.getenv("MAX_TICKET_CHARS", "4000"))
MAX_PROMPT_TOKENS = int(os.getenv("MAX_PROMPT_TOKENS", "3000"))
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "sklearn")

TICKET_CATEGORIES = [
    "Refund",
    "Delivery Delay",
    "Payment",
    "Fraud",
    "Product Quality",
    "App Issue",
    "Other",
]

PRIORITIES = ["Critical", "High", "Medium", "Low"]

RANDOM_SEED = RANDOM_SEED
