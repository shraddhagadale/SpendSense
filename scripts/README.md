# Scripts Directory

This directory contains executable scripts for the SpendSense application.

## Available Scripts

### 1. `process_pdf.py` - PDF to CSV Processor
**Purpose**: Extract transactions from credit card statement PDFs

**Usage**:
```bash
python scripts/process_pdf.py
```

**What it does**:
- Reads PDF from `data/credit_card_statement-2.pdf`
- Automatically detects if PDF is scanned or organic
- Uses OCR if needed (for scanned PDFs)
- Extracts transactions using pattern matching
- Writes results to `data/credit_card_statements.csv`

**Requirements**:
- For scanned PDFs: `ocrmypdf` and Tesseract must be installed

---

### 2. `categorize.py` - Transaction Categorization
**Purpose**: Categorize transactions using LLM

**Usage**:
```bash
python scripts/categorize.py
```

**What it does**:
- Reads transactions from `data/credit_card_statements.csv`
- Uses OpenAI API to categorize each transaction
- Writes categorized results to `data/categorized_transactions.csv`

**Requirements**:
- OpenAI API key in `.env` file

---

### 3. `analytics.py` - Transaction Analytics
**Purpose**: Analyze spending patterns

**Usage**:
```bash
python scripts/analytics.py
```

**What it does**:
- Imports categorized transactions to database
- Shows available months
- Lets you select a month to analyze
- Shows spending breakdown by category
- Shows top transactions for the month

**Requirements**:
- Database must be set up
- Categorized transactions CSV must exist

---

### 4. `migrate_db.py` - Database Migration
**Purpose**: Migrate data from SQLite to PostgreSQL

**Usage**:
```bash
python scripts/migrate_db.py
```

**What it does**:
- Reads data from SQLite database
- Migrates to PostgreSQL database
- Preserves all transaction data

**Requirements**:
- PostgreSQL database configured in `.env`

---

## Typical Workflow

1. **Process PDF** → Extract transactions from statement
   ```bash
   python scripts/process_pdf.py
   ```

2. **Categorize** → Assign categories using LLM
   ```bash
   python scripts/categorize.py
   ```

3. **Analyze** → View spending insights
   ```bash
   python scripts/analytics.py
   ```

---

## Notes

- All scripts should be run from the project root directory
- Make sure dependencies are installed: `pip install -r requirements.txt`
- For OCR support: `brew install tesseract` (macOS)
