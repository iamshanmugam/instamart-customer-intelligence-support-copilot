FEW_SHOT_EXAMPLES = """
Example 1 (anonymised): Customer reports late delivery -> Delivery Delay
Example 2 (anonymised): Payment debited twice -> Payment
Example 3 (anonymised): Request refund for damaged item -> Refund
"""


def zero_shot_prompt(masked_ticket: str) -> str:
    return (
        "You are a support ticket classifier for Instamart.\n"
        "Categories: Refund, Delivery Delay, Payment, Fraud, Product Quality, App Issue, Other.\n"
        f"Ticket:\n{masked_ticket}\n"
        "Return JSON with category and confidence."
    )


def few_shot_prompt(masked_ticket: str) -> str:
    return (
        "You are a support ticket classifier for Instamart.\n"
        f"{FEW_SHOT_EXAMPLES}\n"
        f"Ticket:\n{masked_ticket}\n"
        "Return JSON with category and confidence."
    )
