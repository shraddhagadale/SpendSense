#!/usr/bin/env python3
"""
Transaction Categorization Script

This script categorizes transactions using an LLM (Large Language Model).

Usage:
    python scripts/categorize.py

What it does:
    1. Reads transactions from data/credit_card_statements.csv
    2. Uses LLM to categorize each transaction
    3. Writes categorized results to data/categorized_transactions.csv
"""

import time  
from collections import Counter

from llm_client import LLMAssistant
from spendsense.categories import CATEGORIES
from spendsense.transactions_io import load_transactions_csv, write_transactions_csv
from spendsense.prompts import build_category_prompt


def main():
    """Main entry point for transaction categorization."""
    input_file = "data/credit_card_statements.csv"
    output_file = "data/categorized_transactions.csv"
    
    print("=" * 60)
    print("Transaction Categorization")
    print("=" * 60)
    
    # Load transactions
    transactions = load_transactions_csv(input_file)
    assistant = LLMAssistant()
    categorized = []

    total = len(transactions)
    print(f"\nLoaded {total} transactions from {input_file}")
    print("Categorizing...\n")

    idx_width = len(str(total))

    # Categorize each transaction
    for i, t in enumerate(transactions, start=1):
        description = t["description"]
        amount = t["amount"]

        prompt = build_category_prompt(description, amount, CATEGORIES)
        category = assistant.ask(prompt)
        time.sleep(1)
        categorized.append({**t, "category": category})

        short_desc = (description[:70] + "…") if len(description) > 70 else description
        # Keep columns aligned even as i/total grows (e.g. 9 -> 10 -> 100).
        print(f"[{i:>{idx_width}}/{total}] {category:<16} ${amount:>8.2f}  {short_desc}")

    # Write results
    write_transactions_csv(output_file, categorized)
    
    # Summary statistics
    counts = Counter(t.get("category") or "Unknown" for t in categorized)
    top_counts = ", ".join(f"{k}={v}" for k, v in counts.most_common(5))

    print(f"\n✅ Saved categorized CSV to: {output_file}")
    print(f"✅ Total categorized: {len(categorized)}")
    print(f"📊 Top categories (by count): {top_counts}")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
