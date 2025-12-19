import sqlite3
from datetime import datetime, UTC
from db import get_db_connections
from transactions_loader import load_transactions
from llm_client import LLMAssistant


def import_to_db():
    conn = get_db_connections()
    cursor = conn.cursor()
    transactions = load_transactions()
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
    print("Available months:", months)

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

    
    # Monthly totals accross all months
    monthly_totals = get_monthly_totals(conn)
    print("\nMonthly totals:")
    for month, total in monthly_totals:
        print(f"{month}:{total}")

    # Category totals for the selected month
    cat_totals = get_category_totals_for_month(conn, current_month)
    print(f"\nCategory totals for {current_month}:")
    for category,total in cat_totals:
        print(f"{category}:{total}")

    ## Biggest transactions for the selected month
    top_txns = get_biggest_transactions(conn, current_month, limit=5)
    print(f"\nTop 5 transactions in {current_month}:")
    for date, desc, amount, category in top_txns:
        print(f"{date} | {category} | {amount:.2f} | {desc}")
    

    totals = get_category_totals_for_month(conn, current_month)
    conn.close()

    lines = [f"{category}: {total:.2f}" for category, total in totals]

    summary_text = "\n".join(lines)
    print(summary_text)  # optional: check formatting

    assistant = LLMAssistant()

    prompt = (
        f"Here is the spending per category for {current_month} "
        "(amounts are in your local currency):\n\n"
        f"{summary_text}\n\n"
        "Give a short analysis and 3 concrete suggestions to improve this budget. "
        "Respond in bullet points."
    )

    response = assistant.ask(prompt)
    print("\nLLM analysis:\n")
    print(response)




