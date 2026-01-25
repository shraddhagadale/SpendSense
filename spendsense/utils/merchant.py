"""Merchant name cleaning utilities."""
import re


def clean_merchant_name(description: str) -> str:
    """
    Extract and clean merchant name from raw transaction description.
    
    Examples:
        "AplPay KROGER #339 000000339 INDIANAPOLIS IN" -> "Kroger"
        "LULULEMON ATHLETICA USA B TO C (877)263-9300 CA" -> "Lululemon"
        "AplPay SPEEDWAY 1-800-643-1949 OH" -> "Speedway"
    
    Args:
        description: Raw description from statement
    
    Returns:
        Cleaned merchant name
    """
    text = description.upper()
    
    # Remove payment processors and prefixes
    prefixes = [
        "APLPAY ", "APPLEPAY ", "APPLE PAY ",
        "POS ", "POS PURCHASE ", "PURCHASE ", 
        "DEBIT CARD ", "CHECK CARD ", "CHECKCARD ",
        "VISA ", "MASTERCARD ", "AMEX ", "DISCOVER ",
    ]
    for prefix in prefixes:
        if text.startswith(prefix):
            text = text[len(prefix):]
    
    # Remove common suffixes and noise
    # Remove phone numbers (various formats) - do this FIRST
    text = re.sub(r'\s*1-\d{3}-\d{3}-\d{4}', '', text)  # 1-800-123-4567
    text = re.sub(r'\s*\(\d{3}\)\d{3}-\d{4}', '', text)  # (123)456-7890
    text = re.sub(r'\s*\d{3}-\d{3}-\d{4}', '', text)  # 123-456-7890
    text = re.sub(r'\s*\+?\d{10,}', '', text)  # +12345678901 or 3175798309
    text = re.sub(r'\s+\d{1}-$', '', text)  # Trailing "1-" or similar
    
    # Remove store/location numbers
    text = re.sub(r'\s*#\d+.*$', '', text)  # #339 and everything after
    text = re.sub(r'\s+\d{4,}.*$', '', text)  # Long numbers and everything after
    text = re.sub(r'\s+ST\s+\d+.*$', '', text)  # ST 0000 and after
    text = re.sub(r'\s+MOB\s*$', '', text)  # MOB at end
    
    # Remove state abbreviations (2 capital letters at end or before numbers)
    text = re.sub(r'\s+[A-Z]{2}\s*\d*\s*$', '', text)
    text = re.sub(r'\s+[A-Z]{2}\s+[A-Z\s]+$', '', text)
    
    # Remove common business suffixes
    suffixes = [
        ' USA', ' INC', ' LLC', ' LTD', ' CORP', ' CO',
        ' B TO C', ' CLOTHING', ' AUTO SERVICE', ' GIFT CARD',
        ' FAMILY CLOTHING', ' MARKET', ' GROCERY'
    ]
    for suffix in suffixes:
        if text.endswith(suffix):
            text = text[:-len(suffix)]
    
    # Clean whitespace and title case
    text = ' '.join(text.split())
    return text.title().strip()
