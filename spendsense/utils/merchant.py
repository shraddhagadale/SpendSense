"""Merchant name cleaning utilities."""
import re


def clean_merchant_name(description: str) -> str:
    """
    Extract and clean merchant name from raw transaction description.
    
    Examples:
        "KROGER #1234 COLUMBUS OH" -> "Kroger"
        "POS PURCHASE AMAZON.COM" -> "Amazon.Com"
    
    Args:
        description: Raw description from statement
    
    Returns:
        Cleaned merchant name
    """
    text = description.upper()
    
    # Remove common prefixes
    prefixes = [
        "POS ", "POS PURCHASE ", "PURCHASE ", "DEBIT CARD ",
        "VISA ", "MASTERCARD ", "AMEX ", "DISCOVER ",
        "CHECK CARD ", "CHECKCARD ",
    ]
    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):]
    
    # Remove trailing transaction IDs and numbers
    text = re.sub(r'\s+\d{4,}.*$', '', text)
    text = re.sub(r'\s+#\d+.*$', '', text)
    
    # Remove state abbreviations at end
    text = re.sub(r'\s+[A-Z]{2}\s*$', '', text)
    
    # Clean whitespace and title case
    text = ' '.join(text.split())
    return text.title().strip()
