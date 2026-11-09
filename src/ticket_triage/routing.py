ROUTING_TABLE = {
    "billing": "Payment Support Team",
    "delivery": "Delivery Operations Team",
    "technical": "Technical Support Team",
    "fraud": "Fraud/Security Team",
}

PRIORITY_BY_CATEGORY = {
    "fraud": "Critical",
    "billing": "High",
    "delivery": "Medium",
    "technical": "Medium",
}


def assign_priority(category: str, suggested: str | None = None) -> str:
    cat = str(category).lower()
    if cat == "fraud":
        return "Critical"
    return PRIORITY_BY_CATEGORY.get(cat, suggested or "Medium")


def assign_route(category: str) -> str:
    return ROUTING_TABLE.get(str(category).lower(), "General Support Team")
