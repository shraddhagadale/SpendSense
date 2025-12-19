import csv

def load_transactions():
    transactions = []
    with open("data/categorized_transactions.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["amount"] = float(row["amount"])
            transactions.append(row)
    return transactions

if __name__ == "__main__":
    txs = load_transactions()
    for t in txs:
        print(t)


