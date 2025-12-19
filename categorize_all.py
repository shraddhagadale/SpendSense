import csv
import time  
from transactions_loader import load_transactions
from llm_client import LLMAssistant

categories = ["Food", "Transport","Entertainment","Rent","Utilities","Others"]

def build_prompt(description,amount):
    return(
        "You are a finance expert in categorizaing expenses"
        "Given a transaction description and amount"
        f"select one category from the list: {categories}."
        "Return only the category name."
        f"Description :{description}"
        f"Amount: {amount}"
        "Category:"
    )

if __name__ == "__main__":
    transactions = load_transactions()
    assistant = LLMAssistant()
    categorized = []

    for t in transactions:
        description = t["description"]
        amount = t["amount"]

        prompt = build_prompt(description, amount)
        category = assistant.ask(prompt)
        time.sleep(1)
        categorized.append({**t, "category": category})
        print("\nDescription:",description,"\nAmount:",amount,"\nCategory:",category)

with open("data/categorized_transactions.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["date", "description", "amount", "category"])
    writer.writeheader()
    writer.writerows(categorized)
