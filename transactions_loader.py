import csv

def load_transactions():
    transactions = []
    with open("data/categorized_transactions.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tx = {
                "date": row["date"],
                "description": row["description"],
                "amount": float(row["amount"]),
                "category": row.get("category"),  
            }
            transactions.append(tx)
    return transactions

if __name__ == "__main__":
    txs = load_transactions()
    for t in txs:
        print(t)


