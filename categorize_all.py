import time  
from llm_client import LLMAssistant
from spendsense.categories import CATEGORIES
from spendsense.transactions_io import load_transactions_csv, write_transactions_csv
from spendsense.prompts import build_category_prompt

if __name__ == "__main__":
    input_file = "data/credit_card_statements.csv"
    output_file = "data/categorized_transactions.csv"
    
    transactions = load_transactions_csv(input_file)
    assistant = LLMAssistant()
    categorized = []

    for t in transactions:
        description = t["description"]
        amount = t["amount"]

        prompt = build_category_prompt(description, amount, CATEGORIES)
        category = assistant.ask(prompt)
        time.sleep(1)
        categorized.append({**t, "category": category})
        print("\nDescription:",description,"\nAmount:",amount,"\nCategory:",category)

    write_transactions_csv(output_file, categorized)
    
    print(f"\nCategorized {len(categorized)} transactions and saved to {output_file}")
