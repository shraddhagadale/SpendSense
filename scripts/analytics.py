#!/usr/bin/env python3
"""
Analytics Script

This script provides analytics on categorized transactions.

Usage:
    python scripts/analytics.py

What it does:
    1. Imports categorized transactions to database
    2. Shows available months
    3. Lets you select a month to analyze
    4. Shows spending breakdown by category
    5. Shows top transactions for the month
"""

import sqlite3
from datetime import datetime, UTC
from db import get_db_connections
from spendsense.transactions_io import load_transactions_csv


def import_to_db():
    """Import categorized transactions to database."""
    conn = get_db_connections()
    cursor = conn.cursor()
    transactions = load_transactions_csv("data/categorized_transactions.csv")
    imported_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    

    cursor.executemany("""
                       INSERT OR IGNORE INTO transactions(
                       date,description,amount,category,imported_at)
                       VALUES(?,?,?,?,?)
                       """,
                       [
                            (
                               t['date'], t['description'], t['amount'],t['category'],imported_at
                            )
                             for t in transactions
                        ]
                    )
    conn.commit()
    conn.close()


def get_category_totals(conn):
    """Get total spending by category."""
    cursor = conn.cursor()
    cursor.execute("""
    SELECT category, SUM(amount) AS total
                   FROM transactions
                   GROUP BY category
    """) 
    rows = cursor.fetchall()
    return rows


def get_months(conn):
    """Get available months in the transactions table."""
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT DISTINCT substr(date,1,7) AS month
                    FROM transactions
                    ORDER BY month
                   """
                )
    return [row[0] for row in cursor.fetchall()]


def get_monthly_totals(conn):
    """Get monthly total expenses."""
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT substr(date,1,7) AS month, SUM(amount) AS total
                    FROM transactions
                   GROUP BY month
                   ORDER BY month
                   """)
    return [(row[0],row[1]) for row in cursor.fetchall()]


def get_category_totals_for_month(conn, month):
    """Get category totals for a specific month."""
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT category, SUM(amount) AS total
                    FROM transactions
                    WHERE substr(date,1,7) = ?
                    GROUP BY category
                    ORDER BY total DESC
                   """, (month,))
    return [(row[0],row[1]) for row in cursor.fetchall()]


def get_transactions_for_month(conn, month):
    """Get all transactions for a given month."""
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT date, description, amount, category
                    FROM transactions
                    WHERE substr(date,1,7) = ?
                    ORDER BY date
                   """, (month,))
    return [(row[0],row[1],row[2],row[3]) for row in cursor.fetchall()]


def get_biggest_transactions(conn, month, limit=5):
    """Get top biggest transactions for the month."""
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT date, description, amount, category
                    FROM transactions
                    WHERE substr(date,1,7) = ?
                    ORDER BY ABS(amount) DESC
                    LIMIT 5
                   """, (month,))
    return cursor.fetchall()


def main():
    """Main entry point for analytics."""
    print("=" * 60)
    print("Transaction Analytics")
    print("=" * 60)
    
    # Import data
    print("\nImporting transactions to database...")
    import_to_db()
    conn = get_db_connections()
    
    # Print available months
    months = get_months(conn)
    if not months:
        print("❌ No data found in DB. Run categorize.py first.")
        conn.close()
        raise SystemExit(1)

    print("\n📅 Available months:")
    for idx, m in enumerate(months, start=1):
        print(f"  {idx}. {m}")

    choice = input("\nSelect a month by number (default latest): ").strip()

    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(months):
            current_month = months[idx - 1]
        else:
            current_month = months[-1]
    else:
        current_month = months[-1]

    print(f"\n📊 Analyzing month: {current_month}")
    print("=" * 60)

    # Total spent in the selected month
    month_txns = get_transactions_for_month(conn, current_month)
    selected_total = sum(txn[2] for txn in month_txns)
    print(f"\n💰 Total spent: ${selected_total:.2f}")
    print(f"📝 Transactions: {len(month_txns)}")

    # Category totals for the selected month
    cat_totals = get_category_totals_for_month(conn, current_month)
    print("\n📂 Category breakdown:")
    if cat_totals:
        name_width = max(len(str(c[0] or "")) for c in cat_totals)
        for category, total in cat_totals:
            pct = (total / selected_total * 100) if selected_total else 0
            print(f"  - {category:<{name_width}}  ${total:>10.2f}  ({pct:>5.1f}%)")
    else:
        print("  - (no categories found)")

    # Biggest transactions for the selected month
    top_txns = get_biggest_transactions(conn, current_month, limit=5)
    print("\n🔝 Top 5 transactions:")
    for date, desc, amount, category in top_txns:
        print(f"  {date} | {category:<15} | ${amount:>8.2f} | {desc[:50]}")
    
    print("\n" + "=" * 60)
    conn.close()


if __name__ == "__main__":
    main()
