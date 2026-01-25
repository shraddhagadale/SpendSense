"""LLM prompt templates."""
from spendsense.core import CATEGORIES


def build_category_prompt(description: str, amount: float, categories: list[str] | None = None) -> str:
    """
    Build a prompt for transaction categorization AND merchant extraction.
    
    Args:
        description: Transaction description
        amount: Transaction amount
        categories: List of allowed categories (defaults to CATEGORIES)
    
    Returns:
        Formatted prompt string asking for category and merchant
    """
    if categories is None:
        categories = CATEGORIES
    
    return f"""You are analyzing credit-card transactions. For each transaction, extract TWO pieces of information:
1. Category (from the allowed list)
2. Merchant name (clean, short business name)

Allowed categories (choose EXACTLY one):
{categories}

Category Rules:
- Use the merchant name and context from the description more than the amount.
- Gas stations / fuel purchases → Transport
- Groceries / supermarkets → Grocery
- Restaurants/cafes/fast-food/delivery → Food
- Movies/events/games/amusement → Entertainment
- Rent/lease → Rent
- Power/water/internet/phone bills → Utilities
- Shopping/retail/e-commerce (clothes, electronics, home goods) → Shopping
- Health insurance, pharmacy, medical bills, clinics → Health
- Streaming/music/cloud/app subscriptions → Digital Services
- If unsure → Others

Merchant Extraction Rules:
- Extract the CORE business name only
- Remove: payment processors (AplPay, Apple Pay), phone numbers, addresses, store numbers
- Remove: "USA", "INC", "LLC", state abbreviations, location codes
- Keep it SHORT and CLEAN (2-3 words max)

Examples:
Input: "AplPay KROGER #339 000000339 INDIANAPOLIS IN 3175798309"
Output: {{"category": "Grocery", "merchant": "Kroger"}}

Input: "LULULEMON ATHLETICA USA B TO C (877)263-9300 CA"
Output: {{"category": "Shopping", "merchant": "Lululemon"}}

Input: "AplPay SPEEDWAY 1-800-643-1949 OH 3176304925"
Output: {{"category": "Transport", "merchant": "Speedway"}}

Input: "NETFLIX.COM 1-866-579-7172 CA"
Output: {{"category": "Digital Services", "merchant": "Netflix"}}

Now analyze this transaction. Return ONLY valid JSON with category and merchant:

Description: {description}
Amount: {amount}

JSON:"""
