# SpendSense - Project Structure & Flow Documentation

## 📁 Project Structure

```
SpendSense/
│
├── 📄 README.md                    # Project documentation
├── 📄 ARCHITECTURE.md              # Detailed architecture documentation
├── 📄 pyproject.toml               # Package configuration (PEP 518)
├── 📄 requirements.txt             # Python dependencies
├── 📄 alembic.ini                  # Database migration configuration
├── 📄 .env                         # Environment variables (not in git)
├── 📄 .gitignore                   # Git ignore rules
├── 📄 spendsense.db                # SQLite database
│
├── 📁 spendsense/                  # 🎯 MAIN PACKAGE (reusable code)
│   ├── __init__.py
│   │
│   ├── 📁 services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── ocr.py                  # OCR utilities (detect & process scanned PDFs)
│   │   ├── pdf_processor.py        # PDF processing logic (extract transactions)
│   │   ├── llm.py                  # LLM client (OpenAI API)
│   │   └── prompts.py              # Prompt templates for LLM
│   │
│   ├── 📁 models/                  # Database models (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── base.py                 # Base model class
│   │   ├── transaction.py          # Transaction model
│   │   └── statement.py            # Statement model
│   │
│   ├── 📁 db/                      # Database utilities
│   │   ├── __init__.py
│   │   ├── session.py              # Database session management
│   │   └── repository.py           # Data access layer
│   │
│   ├── 📁 io/                      # Input/Output utilities
│   │   ├── __init__.py
│   │   └── csv.py                  # CSV reading/writing
│   │
│   ├── 📁 config/                  # Configuration
│   │   ├── __init__.py
│   │   └── settings.py             # App settings (reads from .env)
│   │
│   ├── 📁 core/                    # Core utilities
│   │   ├── __init__.py
│   │   └── constants.py            # Application constants
│   │
│   └── 📁 utils/                   # Helper utilities
│       ├── __init__.py
│       ├── dates.py                # Date utilities
│       ├── hashing.py              # Hashing utilities
│       └── merchant.py             # Merchant name cleaning
│
├── 📁 scripts/                     # 🚀 EXECUTABLE SCRIPTS (what you run)
│   ├── __init__.py
│   ├── process_and_categorize.py   # 🎯 ONE-STEP: PDF → Categorized CSV
│   ├── process_pdf.py              # Extract transactions from PDF
│   ├── categorize.py               # Categorize transactions with LLM
│   ├── analytics.py                # Analyze spending patterns
│   └── migrate_db.py               # Migrate SQLite → PostgreSQL
│
├── 📁 tests/                       # 🧪 TESTS
│   ├── __init__.py
│   └── test_ocr.py                 # OCR functionality tests
│
├── 📁 alembic/                     # Database migrations
│   ├── versions/                   # Migration scripts
│   │   └── ad4bf6697a81_create_statements_and_transactions.py
│   ├── env.py                      # Alembic environment
│   ├── script.py.mako              # Migration template
│   └── README                      # Alembic documentation
│
└── 📁 data/                        # 📊 DATA FILES
    ├── credit_card_statement.pdf           # Input PDF (example)
    ├── credit_card_statement-2.pdf         # Input PDF (example)
    ├── credit_card_statements.csv          # Extracted transactions
    └── categorized_transactions.csv        # Categorized transactions
```

---

## 🔄 Complete Workflow & Data Flow

### **⚡ Workflow 0: One-Step Processing (RECOMMENDED)**

This is the **fastest and easiest** way to process PDFs. It combines extraction and categorization into a single command.

```
1. USER places PDF in data/ folder
   ↓
2. USER runs: python scripts/process_and_categorize.py data/statement.pdf
   ↓
3. scripts/process_and_categorize.py
   │
   ├─→ [STEP 1/4] Extract text from PDF
   │   ├─→ Calls: read_pdf_lines()
   │   │   ├─→ Uses: spendsense.services.ocr (auto-detect scanned PDFs)
   │   │   └─→ Uses: PyPDF2.PdfReader (extract text)
   │   └─→ Returns: List of text lines
   │
   ├─→ [STEP 2/4] Combine wrapped transactions
   │   ├─→ Calls: combine_wrapped_transactions()
   │   └─→ Returns: List of complete transaction strings
   │
   ├─→ [STEP 3/4] Parse transaction details
   │   ├─→ Calls: parse_transactions()
   │   └─→ Returns: List of {date, description, amount}
   │
   ├─→ [STEP 4/4] Categorize with AI (in real-time)
   │   ├─→ Uses: spendsense.services.llm.LLMService
   │   ├─→ Uses: spendsense.services.prompts.build_category_prompt
   │   ├─→ For each transaction:
   │   │   ├─→ Build categorization prompt
   │   │   ├─→ Call OpenAI API
   │   │   ├─→ Add category to transaction
   │   │   └─→ Display progress with category
   │   └─→ Returns: Categorized transactions
   │
   └─→ Write to CSV with categories
   ↓
4. OUTPUT: data/statement_categorized.csv
   ✅ Contains: date, description, amount, category (all in one file!)
```

**Benefits:**
- ✅ Single command execution
- ✅ Real-time progress display with categories
- ✅ No intermediate CSV files
- ✅ Automatic OCR detection
- ✅ Category breakdown summary

---

### **🔧 Workflow 1: Multi-Step PDF Processing (Alternative)**

Use this if you want more control or want to process multiple PDFs before categorizing.

```
1. USER places PDF in data/ folder
   ↓
2. USER runs: python scripts/process_pdf.py
   ↓
3. scripts/process_pdf.py
   ├─→ Imports: spendsense.services.pdf_processor
   └─→ Calls: process_pdf(pdf_path)
       ↓
4. spendsense/services/pdf_processor.py
   ├─→ Calls: read_pdf_lines()
   │   ├─→ Uses: spendsense.services.ocr
   │   │   ├─→ is_ocr_available() - Check if OCR installed
   │   │   ├─→ needs_ocr() - Detect if PDF is scanned
   │   │   └─→ process_pdf_with_ocr() - Add text layer if needed
   │   └─→ Uses: PyPDF2.PdfReader - Extract text
   │
   ├─→ Calls: combine_wrapped_transactions()
   │   └─→ Merges multi-line transactions
   │
   └─→ Calls: parse_transactions()
       └─→ Extracts: date, description, amount
   ↓
5. Returns: List of transaction dicts
   ↓
6. scripts/process_pdf.py writes to CSV
   ↓
7. OUTPUT: data/credit_card_statements.csv
```

### **Workflow 2: Categorization**

```
1. USER runs: python scripts/categorize.py
   ↓
2. scripts/categorize.py
   ├─→ Reads: data/credit_card_statements.csv
   ├─→ Uses: spendsense.services.llm (OpenAI API)
   ├─→ Uses: spendsense.services.prompts
   └─→ For each transaction:
       ├─→ Build prompt with description + amount
       ├─→ Ask LLM for category
       └─→ Append category to transaction
   ↓
3. OUTPUT: data/categorized_transactions.csv
```

### **Workflow 3: Analytics**

```
1. USER runs: python scripts/analytics.py
   ↓
2. scripts/analytics.py
   ├─→ Reads: data/categorized_transactions.csv
   ├─→ Imports to database (SQLite/PostgreSQL)
   ├─→ Queries database for insights:
   │   ├─→ Monthly totals
   │   ├─→ Category breakdown
   │   └─→ Top transactions
   └─→ Displays results
```

---

## 📚 What Each Component Does

### **Services** (`spendsense/services/`)

These are **reusable business logic modules** that can be imported by scripts.

| File | Purpose | Key Functions |
|------|---------|---------------|
| `ocr.py` | OCR utilities | `is_ocr_available()`, `needs_ocr()`, `process_pdf_with_ocr()` |
| `pdf_processor.py` | PDF processing | `process_pdf()`, `read_pdf_lines()`, `parse_transactions()` |
| `llm.py` | LLM client | `LLMService.ask()` |
| `prompts.py` | Prompt templates | `build_category_prompt()` |

**Why separate?**
- ✅ Reusable across multiple scripts
- ✅ Easier to test
- ✅ Clean separation of concerns

---

### **Scripts** (`scripts/`)

These are **executable entry points** - what you run from the command line.

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `process_pdf.py` | Extract transactions | PDF file | CSV file |
| `categorize.py` | Categorize transactions | CSV file | Categorized CSV |
| `analytics.py` | Analyze spending | Categorized CSV | Console output |
| `migrate_db.py` | Migrate database | SQLite DB | PostgreSQL DB |

**Why separate?**
- ✅ Clear entry points for users
- ✅ Thin wrappers around services
- ✅ Easy to understand what to run

---

### **Models** (`spendsense/models/`)

Database models using SQLAlchemy ORM.

| Model | Purpose | Fields |
|-------|---------|--------|
| `Transaction` | Single transaction | date, amount, description, category, merchant |
| `Statement` | Uploaded PDF | filename, file_hash, uploaded_at |

---

### **Tests** (`tests/`)

Test files to verify functionality.

| Test File | Purpose |
|-----------|---------|
| `test_ocr.py` | Verify OCR setup and functionality |
| `test_pdf_processor.py` | Test PDF extraction logic |

---

## 🎯 OCR Flow (Detailed)

### **What is `ocr.py`?**

`spendsense/services/ocr.py` is a **helper module** that provides OCR functionality.

**It does NOT process PDFs directly** - it just adds a searchable text layer to scanned PDFs so that PyPDF2 can extract text.

### **OCR Flow:**

```
1. pdf_processor.py calls: read_pdf_lines(pdf_path)
   ↓
2. Check: is_ocr_available()?
   ├─→ YES: Continue
   └─→ NO: Skip OCR, try direct extraction
   ↓
3. Check: needs_ocr(pdf_path)?
   ├─→ YES (scanned): PDF has < 100 chars of text
   └─→ NO (organic): PDF has extractable text
   ↓
4. If scanned: process_pdf_with_ocr(pdf_path)
   ├─→ Uses: ocrmypdf library
   ├─→ Uses: Tesseract OCR engine
   ├─→ Creates: Temporary PDF with text layer
   └─→ Returns: Path to processed PDF
   ↓
5. PyPDF2 extracts text from:
   ├─→ Original PDF (if organic)
   └─→ Processed PDF (if scanned)
   ↓
6. Clean up temporary files
   ↓
7. Return: List of text lines
```

### **Why is OCR in a separate file?**

- ✅ **Reusability**: Other scripts can use OCR too
- ✅ **Testability**: Easy to test OCR in isolation
- ✅ **Maintainability**: OCR logic is in one place
- ✅ **Optional**: Can disable OCR without breaking PDF processing

---

## 🚀 How to Use

### **1. Process a PDF**
```bash
# Place your PDF in data/ folder
cp ~/Downloads/statement.pdf data/

# Run processor
python scripts/process_pdf.py

# Output: data/credit_card_statements.csv
```

### **2. Categorize Transactions**
```bash
# Make sure you have OpenAI API key in .env
python scripts/categorize.py

# Output: data/categorized_transactions.csv
```

### **3. Analyze Spending**
```bash
python scripts/analytics.py

# Interactive: Select month and view insights
```

### **4. Run Tests**
```bash
# Test OCR functionality
python tests/test_ocr.py

# Or use pytest
pytest tests/
```

---

## 🔧 Installation

### **1. Install System Dependencies**
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr
```

### **2. Install Python Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Install Package in Development Mode**
```bash
pip install -e .
```

### **4. Set Up Environment**
```bash
# Create .env file
cp .env.example .env

# Add your API keys
OPENAI_API_KEY=your_key_here
```

---

## 📊 Key Design Decisions

### **Why this structure?**

1. **Separation of Concerns**
   - Services = Business logic (reusable)
   - Scripts = Entry points (what users run)
   - Models = Data structures
   - Tests = Verification

2. **Scalability**
   - Easy to add new services
   - Easy to add new scripts
   - Easy to add new models

3. **Maintainability**
   - Each file has a single responsibility
   - Easy to find where code lives
   - Easy to test individual components

4. **Industry Standard**
   - Follows Python packaging best practices
   - Similar to Django, Flask, FastAPI projects
   - Easy for other developers to understand

---

## 🎓 Learning Path

If you're new to this structure, read files in this order:

1. **scripts/process_pdf.py** - See what the user runs
2. **spendsense/services/pdf_processor.py** - See the core logic
3. **spendsense/services/ocr.py** - See how OCR works
4. **tests/test_ocr.py** - See how to test

---

## 📝 Summary

| Location | What | Why |
|----------|------|-----|
| `spendsense/services/` | Business logic | Reusable, testable |
| `scripts/` | Executable scripts | What users run |
| `spendsense/models/` | Database models | Data structure |
| `tests/` | Test files | Verification |
| `data/` | Input/output files | Data storage |

**Remember**: 
- **Services** = Tools (you import them)
- **Scripts** = Actions (you run them)
