# SpendSense

AI-powered expense tracking and analytics for credit card statements.

## Overview

SpendSense automatically processes credit card statement PDFs, categorizes transactions using AI, and provides spending analytics. It handles both digital and scanned documents through integrated OCR.

## Features

- PDF transaction extraction with OCR support
- AI-powered transaction categorization
- Merchant name extraction
- Spending analytics and insights
- SQLite and PostgreSQL database support
- Deduplication and data integrity

## Installation

### Prerequisites

- Python 3.11 or higher
- Tesseract OCR
- OpenAI API key

### Setup

```bash
git clone https://github.com/shraddhagadale/SpendSense.git
cd SpendSense

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install Tesseract
brew install tesseract  # macOS
# sudo apt-get install tesseract-ocr  # Linux
```

### Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key
DB_TYPE=sqlite
SQLITE_PATH=spendsense.db
```

## Usage

### Process a Statement

```bash
python scripts/process_and_categorize.py --input file_path
```

### View Analytics

```bash
python scripts/analytics.py
```

## Project Structure

```
SpendSense/
├── spendsense/          # Core library
│   ├── services/        # Business logic
│   ├── models/          # Database models
│   ├── db/              # Database layer
│   └── utils/           # Utilities
├── scripts/             # CLI scripts
├── tests/               # Tests
└── alembic/             # Database migrations
```

### Currently in Development

- [ ] Web UI for visualizations
- [ ] AI assistant for transaction queries
- [ ] Budget tracking
- [ ] Multi-currency support
- [ ] Mobile application

