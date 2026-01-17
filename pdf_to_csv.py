import re
import csv
from PyPDF2 import PdfReader  # pip install PyPDF2


# Pattern: lines that START a transaction (your dates look like 11/01/25)
DATE_LINE = re.compile(
    r"""^\s*(
        \d{1,2}            # day or month
        [/\-]              # separator
        \d{1,2}
        (?:[/\-]\d{2,4})?  # optional year
    )\b""",
    re.VERBOSE,
)
# Pattern to pull date, description, amount from the *combined* line
# Example combined line:
# "11/01/25 ABC*NATIONAL INSTITUTE F INDIANAPOLIS IN 317-274-3432 $39.50"
TXN_PATTERN = re.compile(
    r"^\s*(\d{2}/\d{2}/\d{2})\s+(.+?)\s+(-?\$?\d+\.\d{2})\s*$"
)


def read_pdf_lines(path: str) -> list[str]:
    reader = PdfReader(path)
    all_lines: list[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""
        all_lines.extend(text.splitlines())

    # keep only the "New Charges Details" section
    filtered: list[str] = []
    in_details = False
    for line in all_lines:
        if "New Charges Details" in line:
            in_details = True
            continue
        if in_details and line.strip().startswith(("Fees", "Interest", "About ")):
            in_details = False
        if in_details:
            filtered.append(line)

    return filtered


def combine_wrapped_transactions(lines: list[str]) -> list[str]:
    """
    Combine 2-line transactions into one string.

    Example input lines (like your sample):

    018: 11/01/25 ABC*NATIONAL INSTITUTE F  INDIANAPOLIS  IN
    019: 317-274-3432 $39.50
    """
    records: list[str] = []
    current: str | None = None

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        if DATE_LINE.match(line):
            # new transaction starts
            if current:
                records.append(current)
            current = line
        else:
            # continuation of previous transaction
            if current:
                current = current + " " + line

    if current:
        records.append(current)

    return records


def parse_transactions(records: list[str]) -> list[dict]:
    """
    From combined records, extract date, description, amount.
    """
    txns: list[dict] = []

    for rec in records:
        m = TXN_PATTERN.match(rec)
        if not m:
            # You can print rec here for debugging if needed
            # print("NO MATCH:", rec)
            continue

        date, middle, amount = m.groups()

        # Normalise amount: drop $ sign
        amount = amount.replace("$", "")

        # You can further clean description: e.g. keep everything,
        # or later strip phone numbers using another regex.
        description = middle.strip()

        txns.append(
            {
                "date": date,
                "description": description,
                "amount": amount,
            }
        )

    return txns


def write_csv(transactions: list[dict], csv_path: str) -> None:
    """Write transactions to a CSV file."""
    fieldnames = ["date", "description", "amount"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)


import os

def main():
    pdf_path = "data/credit_card_statement-2.pdf"
    # Keep this consistent with categorize_all.py input_file to avoid manual renaming.
    csv_path = "data/credit_card_statements.csv"

    lines = read_pdf_lines(pdf_path)
    records = combine_wrapped_transactions(lines)

    print("Combined records:")
    for r in records:
        print(">>>", r)

    transactions = parse_transactions(records)
    print("Parsed transactions:", len(transactions))
    for t in transactions:
        print(t)

    write_csv(transactions, csv_path)
    print(f"Wrote {len(transactions)} transactions to {csv_path}")



if __name__ == "__main__":
    main()

