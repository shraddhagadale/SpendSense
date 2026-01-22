"""LLM prompt templates."""
from spendsense.core import CATEGORIES


def build_category_prompt(description: str, amount: float, categories: list[str] | None = None) -> str:
    """
    Build a strict classification prompt for transaction categorization.
    
    Args:
        description: Transaction description
        amount: Transaction amount
        categories: List of allowed categories (defaults to CATEGORIES)
    
    Returns:
        Formatted prompt string
    """
    if categories is None:
        categories = CATEGORIES
    
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
