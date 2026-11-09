"""CLI for ticket classification with guardrails."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.ticket_triage import classify_ticket


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify a support ticket")
    parser.add_argument("text", nargs="?", default="", help="Ticket text")
    parser.add_argument("--file", type=Path, help="Read ticket from file")
    parser.add_argument(
        "--strategy", choices=["zero_shot", "few_shot"], default="zero_shot"
    )
    args = parser.parse_args()
    text = args.text
    if args.file:
        text = args.file.read_text(encoding="utf-8")
    result = classify_ticket(text, strategy=args.strategy)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
