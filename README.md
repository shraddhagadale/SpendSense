# SpendSense 💰

> AI-powered expense tracking with automatic transaction categorization and merchant extraction

Transform your credit card statements into actionable insights. SpendSense uses cutting-edge AI to automatically extract, categorize, and analyze your spending—all from a simple PDF upload.

---

## ✨ Features

- 📄 **Smart PDF Processing** - Extracts transactions from any credit card statement
- 🔍 **OCR Support** - Handles both digital and scanned PDFs seamlessly
- 🤖 **AI-Powered Categorization** - Uses OpenAI LLM to intelligently categorize every transaction
- 🏪 **Intelligent Merchant Extraction** - No regex, just pure AI understanding
- 📊 **Analytics Dashboard** - Discover your spending patterns
- 💾 **Flexible Database** - PostgreSQL or SQLite support
- 🏗️ **Production-Ready** - Clean architecture, type-safe, well-tested

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Tesseract OCR (for scanned PDFs)
- OpenAI API key

### Installation

```bash
# Clone and setup
git clone https://github.com/shraddhagadale/SpendSense.git
cd SpendSense

# Install Tesseract
brew install tesseract  # macOS
# sudo apt-get install tesseract-ocr  # Linux

# Setup Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Configure
cp .env.example .env
# Add your OPENAI_API_KEY to .env
```

### Usage

```bash
# Process your statement
python scripts/process_and_categorize.py --input data/statement.pdf

# Explore your spending
python scripts/analytics.py
```

That's it! SpendSense handles the rest.

---

## 💡 How It Works

SpendSense uses a sophisticated AI pipeline to transform raw PDFs into structured insights:

1. **Intelligent Extraction** - Automatically detects and extracts transactions, with OCR for scanned documents
2. **AI Understanding** - OpenAI's LLM analyzes each transaction to determine category and merchant
3. **Smart Storage** - Deduplication and structured storage in your choice of database
4. **Powerful Analytics** - Query and visualize your spending patterns

## 📁 Project Structure

```
SpendSense/
├── spendsense/          # Core library
│   ├── services/        # PDF, OCR, LLM services
│   ├── models/          # Database models
│   ├── db/              # Database layer
│   └── utils/           # Helpers
├── scripts/             # CLI tools
├── tests/               # Test suite
└── alembic/             # Migrations
```

Clean, modular, maintainable.

---

## 🔧 Configuration

Create `.env` with your settings:

```env
# OpenAI
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=model_name

# Database (SQLite or PostgreSQL)
DB_TYPE=sqlite
SQLITE_PATH=spendsense.db
```

---

## 🎯 Supported Categories

Grocery • Food • Transport • Shopping • Entertainment • Health • Utilities • Rent • Digital Services • Others

The AI learns and adapts to your spending patterns.

---

## Future Roadmap

### Currently in Development

- ** Interactive Web UI** - Beautiful visualizations and dashboards for your spending data
- **🤖 AI Assistant** - Ask questions about your transactions and get personalized budgeting advice
  - *"How much did I spend on groceries last month?"*
  - *"Show me all my Starbucks purchases"*
  - *"What's my average monthly spending on transport?"*
  - *"Should I cut back on dining out? Give me budgeting advice"*
  - *"Help me create a budget based on my spending patterns"*

---

## 🗄️ Database Options

### SQLite (Default)
Perfect for personal use. Zero configuration.

### PostgreSQL
For production deployments:

```bash
createdb spendsense
alembic upgrade head
```

---