FEW_SHOT_BLOCK = """
EXAMPLES:
Ticket: unauthorized charge on my card -> fraud
Ticket: app crashes on login -> technical
Ticket: charged twice for order -> billing
Ticket: delivery very late -> delivery
"""


def build_classify_messages(masked_ticket: str, few_shot: bool = False) -> list[dict]:
    system = "CLASSIFY. Return JSON with category and reason."
    if few_shot:
        system += FEW_SHOT_BLOCK
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": masked_ticket},
    ]
