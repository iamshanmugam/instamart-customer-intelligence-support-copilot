ROUTING_TABLE = {
    "Refund": "Refund Support Team",
    "Delivery Delay": "Delivery Operations Team",
    "Payment": "Payment Support Team",
    "Fraud": "Fraud/Security Team",
    "Product Quality": "Quality Support Team",
    "App Issue": "Technical Support Team",
    "Other": "General Support Team",
}

PRIORITY_BY_CATEGORY = {
    "Fraud": "Critical",
    "Payment": "High",
    "Refund": "High",
    "Delivery Delay": "Medium",
    "Product Quality": "Medium",
    "App Issue": "Medium",
    "Other": "Low",
}


def assign_priority(category: str, suggested: str | None = None) -> str:
    if suggested in ("Critical", "High", "Medium", "Low"):
        if category == "Fraud" and suggested != "Critical":
            return "Critical"
        return suggested
    return PRIORITY_BY_CATEGORY.get(category, "Low")


def assign_route(category: str) -> str:
    return ROUTING_TABLE.get(category, "General Support Team")
