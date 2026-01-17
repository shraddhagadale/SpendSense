import csv
import time  
from transactions_loader import load_transactions
from llm_client import LLMAssistant

categories = ["Grocery","Food", "Transport", "Entertainment", "Digital Services","Rent", "Utilities", "Shopping","Health","Others"]

def build_prompt(description,amount):
    # Keep this prompt very explicit: rules + examples + strict output format.
    # The model must return EXACTLY one category string from `categories`.
    return f"""You are categorizing credit-card transactions into EXACTLY ONE category.

Allowed categories (return EXACTLY one of these, spelled exactly):
{categories}

Rules:
- Use the merchant name and context from the description more than the amount.
- If the description looks like a gas station / fuel purchase, classify as Transport.
- If the description is groceries / supermarkets, classify as Grocery.
- If it's a restaurant/cafe/fast-food/delivery purchase, classify as Food.
- If it's movies/events/games/amusement, classify as Entertainment.
- If it's rent/lease, classify as Rent.
- If it's power/water/internet/phone bills, classify as Utilities.
- If it's shopping/retail/e-commerce (clothes, shoes, electronics, home goods), classify as Shopping.
- If it's health insurance, pharmacy, medical bills, clinics, etc., classify as Health.
- If it's streaming/music/cloud/app subscriptions (Netflix, Spotify, Apple/Google subscriptions), classify as Digital Services.
- If unsure, use Others.

Examples (learn these patterns):
- "KROGER", "WHOLE FOODS", "TRADER JOE'S", "SAFEWAY" -> Grocery
- "SPEEDWAY", "SHELL", "BP", "EXXON", "CHEVRON" -> Transport (gas/fuel)
- "UBER", "LYFT", "METRO", "PARKING" -> Transport
- "AMC THEATRES", "REGAL", "STEAM", "PLAYSTATION", "XBOX" -> Entertainment
- "NETFLIX", "SPOTIFY", "HULU", "APPLE.COM/BILL", "GOOGLE *SERVICES", "ICLOUD" -> Digital Services
- "AMAZON", "AMZN", "LULULEMON", "TARGET", "WALMART", "NIKE" -> Shopping
- "CVS", "WALGREENS", "UNITED HEALTH", "KAISER", "HOSPITAL", "CLINIC" -> Health
- "RENT", "APARTMENTS", "PROPERTY MGMT" -> Rent
- "ELECTRIC", "WATER", "COMCAST", "VERIZON", "AT&T" -> Utilities

Now categorize this transaction. Return ONLY the category name.

Description: {description}
Amount: {amount}
Category:"""

if __name__ == "__main__":
    input_file = "data/credit_card_statements.csv"
    output_file = "data/categorized_transactions.csv"
    
    transactions = load_transactions(input_file)
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

    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "description", "amount", "category"])
        writer.writeheader()
        writer.writerows(categorized)
    
    print(f"\n✅ Categorized {len(categorized)} transactions and saved to {output_file}")
