# SpendSense 💰

> Personal expense tracking and analytics with AI-powered categorization

SpendSense automatically extracts transactions from credit card statement PDFs, categorizes them using AI, and provides insightful spending analytics. Supports both text-based and scanned PDFs with built-in OCR.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

- 📄 **PDF Processing** - Extract transactions from credit card statements
- 🔍 **OCR Support** - Automatically handles scanned PDFs using Tesseract
- 🤖 **AI Categorization** - Categorize transactions using OpenAI's LLM
- 📊 **Analytics** - Visualize spending patterns by category and time
- 💾 **Database Storage** - PostgreSQL/SQLite support with migrations
- 🏗️ **Clean Architecture** - Industry-standard Python project structure

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Tesseract OCR (for scanned PDFs)
- OpenAI API key (for categorization)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/shraddhagadale/SpendSense.git
cd SpendSense

# 2. Install Tesseract (for OCR support)
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install package in development mode
pip install -e .

# 5. Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Usage

```bash
# 1. Extract transactions from PDF
python scripts/process_pdf.py

# 2. Categorize transactions with AI
python scripts/categorize.py

# 3. View spending analytics
python scripts/analytics.py
```

---

## 📖 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete project structure and flow explanation
- **[scripts/README.md](scripts/README.md)** - Detailed usage of each script
- **[OCR Setup Guide](#ocr-setup)** - How to configure OCR for scanned PDFs

---

## 🔄 Workflow

```
1. Place PDF in data/ folder
   ↓
2. Run: python scripts/process_pdf.py
   → Extracts transactions to CSV
   → Automatically uses OCR for scanned PDFs
   ↓
3. Run: python scripts/categorize.py
   → Categorizes transactions using AI
   ↓
4. Run: python scripts/analytics.py
   → View spending insights
```

---

## 📁 Project Structure

```
SpendSense/
├── spendsense/          # Main package (reusable code)
│   ├── services/        # Business logic (OCR, PDF processing, LLM)
│   ├── models/          # Database models
│   ├── db/              # Database utilities
│   └── config/          # Configuration
│
├── scripts/             # Executable scripts
│   ├── process_pdf.py   # Extract transactions from PDF
│   ├── categorize.py    # Categorize with AI
│   └── analytics.py     # View analytics
│
├── tests/               # Test files
└── data/                # Input PDFs and output CSVs
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

---

## 🔧 Configuration

Create a `.env` file in the project root:

```env
# OpenAI API (for categorization)
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1/chat/completions

# Database (PostgreSQL or SQLite)
DB_TYPE=sqlite
SQLITE_PATH=spendsense.db

# Or use PostgreSQL
# DB_TYPE=postgres
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432
# POSTGRES_DB=spendsense
# POSTGRES_USER=your_user
# POSTGRES_PASSWORD=your_password
```

---

## 🧪 Testing

```bash
# Test OCR functionality
python tests/test_ocr.py

# Run all tests with pytest
pytest tests/
```

---

## 📊 Example Output

### PDF Processing
```
============================================================
PDF to CSV Processor
============================================================
✅ OCR support: Available (will auto-detect scanned PDFs)

Processing: data/credit_card_statement-2.pdf
✅ Extracted 22 transactions
✅ Wrote CSV to: data/credit_card_statements.csv
```

### Categorization
```
============================================================
Transaction Categorization
============================================================

Loaded 22 transactions from data/credit_card_statements.csv
Categorizing...

[ 1/22] Groceries        $   39.50  ABC*NATIONAL INSTITUTE F INDIANAPOLIS IN
[ 2/22] Dining           $   15.20  STARBUCKS #12345 NEW YORK NY
...
✅ Saved categorized CSV to: data/categorized_transactions.csv
```

### Analytics
```
============================================================
Transaction Analytics
============================================================

📊 Analyzing month: 2025-01

💰 Total spent: $1,234.56
📝 Transactions: 22

📂 Category breakdown:
  - Groceries      $  450.00  (36.4%)
  - Dining         $  320.00  (25.9%)
  - Transportation $  180.00  (14.6%)
  - Entertainment  $  150.00  (12.1%)
  - Other          $  134.56  (10.9%)
```

---

## 🔍 OCR Setup

SpendSense automatically detects if a PDF is scanned and applies OCR when needed.

### How It Works

1. **Organic PDFs** (text-based) - Extracts text directly ⚡
2. **Scanned PDFs** (image-based) - Automatically applies OCR 🔍

### Verify OCR Installation

```bash
# Check if Tesseract is installed
tesseract --version

# Test OCR functionality
python tests/test_ocr.py
```

### Supported Languages

Default: English (`eng`)

To add more languages:
```bash
# macOS
brew install tesseract-lang

# Ubuntu/Debian
sudo apt-get install tesseract-ocr-spa  # Spanish
sudo apt-get install tesseract-ocr-fra  # French
```

---

## 🛠️ Development

### Install Development Dependencies

```bash
pip install -r requirements.txt
pip install -e ".[dev]"
```

### Code Style

This project uses:
- **Ruff** for linting and formatting
- **Type hints** for better code quality
- **Docstrings** for documentation

```bash
# Run linter
ruff check .

# Format code
ruff format .
```

---

## 🗄️ Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Migrate from SQLite to PostgreSQL
python scripts/migrate_db.py
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🙏 Acknowledgments

- **[ocrmypdf](https://github.com/ocrmypdf/OCRmyPDF)** - OCR for scanned PDFs
- **[Tesseract OCR](https://github.com/tesseract-ocr/tesseract)** - OCR engine
- **[OpenAI](https://openai.com/)** - AI-powered categorization
- **[PyPDF](https://github.com/py-pdf/pypdf)** - PDF text extraction

---

## 📧 Contact

**Shraddha Gadale** - [@shraddhagadale](https://github.com/shraddhagadale)

Project Link: [https://github.com/shraddhagadale/SpendSense](https://github.com/shraddhagadale/SpendSense)

---

<div align="center">
Made with ❤️ by Shraddha Gadale
</div>
