import sqlite3
from datetime import datetime, UTC
from db import get_db_connections
from spendsense.transactions_io import load_transactions_csv


def import_to_db():
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
    cursor = conn.cursor()
    cursor.execute("""
    SELECT category, SUM(amount) AS total
                   FROM transactions
                   GROUP BY category
    """) 
    rows = cursor.fetchall()
    return rows

## Available months in the transactions table
def get_months(conn):
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT DISTINCT substr(date,1,7) AS month
                    FROM transactions
                    ORDER BY month
                   """
                )
    return [row[0] for row in cursor.fetchall()]

## Monthly total expenses
def get_monthly_totals(conn):
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT substr(date,1,7) AS month, SUM(amount) AS total
                    FROM transactions
                   GROUP BY month
                   ORDER BY month
                   """)
    return [(row[0],row[1]) for row in cursor.fetchall()]

## Category total for a month 
def get_category_totals_for_month(conn, month):
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT category, SUM(amount) AS total
                    FROM transactions
                    WHERE substr(date,1,7) = ?
                    GROUP BY category
                    ORDER BY total DESC
                   """, (month,))
    return [(row[0],row[1]) for row in cursor.fetchall()]

## Transactions for a given month 
def get_transactions_for_month(conn, month):
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT date, description, amount, category
                    FROM transactions
                    WHERE substr(date,1,7) = ?
                    ORDER BY date
                   """, (month,))
    return [(row[0],row[1],row[2],row[3]) for row in cursor.fetchall()]

## top biggest transactions for the month
def get_biggest_transactions(conn, month, limit=5):
    cursor = conn.cursor()
    cursor.execute("""
                    SELECT date, description, amount, category
                    FROM transactions
                    WHERE substr(date,1,7) = ?
                    ORDER BY ABS(amount) DESC
                    LIMIT 5
                   """, (month,))
    return cursor.fetchall()



if __name__ == "__main__":
    
    import_to_db()
    conn = get_db_connections()
    
    # Print available months
    months = get_months(conn)
    if not months:
        print("No data found in DB. Run categorize_all.py first, then re-run analytics.py.")
        conn.close()
        raise SystemExit(1)

    print("\nAvailable months:")

    for idx, m in enumerate(months, start=1):
        print(f"{idx}. {m}")

    choice = input("Select a month by number (default latest): ").strip()

    if choice.isdigit():
        idx = int(choice)
        if 1 <= idx <= len(months):
            current_month = months[idx - 1]
        else:
            current_month = months[-1]
    else:
        current_month = months[-1]

    print(f"\nAnalyzing month: {current_month}")

    # Total spent in the selected month (from raw transactions)
    month_txns = get_transactions_for_month(conn, current_month)
    selected_total = sum(txn[2] for txn in month_txns)
    print(f"Total spent: {selected_total:.2f}")
    print(f"Transactions: {len(month_txns)}")

    # Category totals for the selected month
    cat_totals = get_category_totals_for_month(conn, current_month)
    print("\nCategory totals:")
    if cat_totals:
        name_width = max(len(str(c[0] or "")) for c in cat_totals)
        for category, total in cat_totals:
            pct = (total / selected_total * 100) if selected_total else 0
            print(f"- {category:<{name_width}}  {total:>10.2f}  ({pct:>5.1f}%)")
    else:
        print("- (no categories found)")

    ## Biggest transactions for the selected month
    top_txns = get_biggest_transactions(conn, current_month, limit=5)
    print("\nTop 5 transactions:")
    for date, desc, amount, category in top_txns:
        print(f"{date} | {category} | {amount:.2f} | {desc}")
    

    conn.close()




