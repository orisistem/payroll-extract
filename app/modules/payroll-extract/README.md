# PayrollExtract 💼

**Smart Payroll Data Extraction with Clean Architecture**

A professional Python system for extracting, processing, and storing payroll data from PDF files using Clean Architecture principles and SOLID design patterns.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Architecture: Clean](https://img.shields.io/badge/Architecture-Clean-green.svg)](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

---

## 🏗️ Architecture Overview

This project follows **Clean Architecture** principles with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│                      (main.py, CLI)                      │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────┐
│                    Service Layer                         │
│              (Business Logic Orchestration)              │
│                   PayrollService                         │
└─────┬──────────────┬──────────────┬─────────────────────┘
      │              │              │
┌─────▼─────┐ ┌─────▼──────┐ ┌────▼──────────┐
│  Parsers  │ │Repositories│ │   Exporters    │
│           │ │            │ │                │
│ PDFParser │ │SQLiteRepo  │ │  CSVExporter   │
│DateParser │ │            │ │ JSONExporter   │
│ EmpParser │ │            │ │                │
└─────┬─────┘ └─────┬──────┘ └────┬───────────┘
      │              │              │
┌─────▼──────────────▼──────────────▼─────────┐
│              Domain Layer                    │
│    (Entities & Value Objects)                │
│  Employee, Payroll, Money, PayrollPeriod     │
└──────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
payroll-extract/
│
├── domain/                      # 🎯 Domain Layer
│   ├── __init__.py
│   ├── money.py                # Money value object (immutable)
│   ├── payroll_period.py       # Period value object
│   ├── employee.py             # Employee entity
│   └── payroll.py              # Payroll aggregate root
│
├── parsers/                     # 📄 Parser Layer
│   ├── __init__.py
│   ├── text_line.py            # TextLine value object
│   ├── text_parser.py          # PDF text extraction
│   ├── money_parser.py         # Monetary value parsing
│   ├── date_parser.py          # Date detection (Strategy pattern)
│   ├── employee_parser.py      # Employee data extraction
│   └── pdf_parser.py           # Main parser orchestrator
│
├── repositories/                # 💾 Repository Layer
│   ├── __init__.py
│   ├── payroll_repository.py   # Abstract repository interface
│   └── sqlite_repository.py    # SQLite implementation
│
├── exporters/                   # 📤 Exporter Layer
│   ├── __init__.py
│   ├── payroll_exporter.py     # Abstract exporter interface
│   ├── csv_exporter.py         # CSV export implementation
│   └── json_exporter.py        # JSON export implementation
│
├── services/                    # 🎭 Service Layer
│   ├── __init__.py
│   └── payroll_service.py      # Business logic orchestration
│
├── main.py                      # 🚀 Application entry point
├── requirements.txt             # 📦 Dependencies
└── README.md                    # 📖 This file
```

---

## 🎯 Clean Architecture Layers

### 1. **Domain Layer** (Core Business Logic)

**Purpose:** Contains enterprise business rules and domain entities.

#### `Money` (Value Object)

- Immutable monetary value with currency
- Brazilian format support (1.234,56)
- Arithmetic operations (+, -, \*, /)
- Type-safe financial calculations

#### `PayrollPeriod` (Value Object)

- Represents month/year (e.g., 09/2024)
- Immutable with validation
- Conversion methods (to_string, get_full_name)

#### `Employee` (Entity)

- Unique employee with 6-digit ID
- Contains: name, position, gross/net values, page
- Business rules validation
- Calculate deductions and percentages

#### `Payroll` (Aggregate Root)

- Collection of employees for a period
- Manages totals and averages
- Ensures consistency
- Provides filtering and sorting

---

### 2. **Parser Layer** (Data Extraction)

**Purpose:** Extracts and transforms PDF data into domain objects.

#### `TextParser`

- Extracts text from PDF using PyMuPDF
- Normalizes lines and removes accents
- Returns `TextLine` value objects

#### `MoneyParser`

- Finds monetary values in text
- Brazilian format support
- Returns `Money` domain objects

#### `DateParser` (Strategy Pattern)

- Multiple detection strategies
- Priority-based selection
- Detects: Competência, Referência, Month names, etc.
- Environment variable override support

#### `EmployeeParser`

- Identifies employee blocks (6-digit code)
- Extracts name, position, values
- Applies business rules
- Returns `Employee` domain objects

#### `PDFParser` (Orchestrator)

- Coordinates all parsers
- Main entry point for parsing
- Returns complete `Payroll` aggregate

---

### 3. **Repository Layer** (Persistence)

**Purpose:** Abstract data access with multiple implementations.

#### `PayrollRepository` (Interface)

- Abstract base class
- Defines: save, find_by_period, find_all, delete, exists
- Enables dependency inversion

#### `SQLitePayrollRepository` (Implementation)

- SQLite-based persistence
- Two tables: payroll + employee
- Foreign key relationships
- Transaction support

**Easy to extend:** Create `PostgreSQLRepository`, `MongoRepository`, etc.

---

### 4. **Exporter Layer** (Output Generation)

**Purpose:** Export payroll data to different formats.

#### `PayrollExporter` (Interface)

- Abstract base class
- Single method: export(payroll, output_path)

#### `CSVExporter`

- Optional summary header
- Formatted employee table
- Deduction calculations

#### `JSONExporter`

- Structured JSON output
- Pretty-print option
- Complete payroll data

**Easy to extend:** Add `XMLExporter`, `ExcelExporter`, etc.

---

### 5. **Service Layer** (Business Logic)

**Purpose:** Orchestrates use cases and coordinates layers.

#### `PayrollService`

- Main business logic coordinator
- Dependency injection
- Use cases:
  - `process_payroll()`: Parse and optionally save
  - `get_payroll()`: Retrieve by period
  - `export_payroll()`: Export to format
  - `delete_payroll()`: Remove by period

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 💻 Usage

### Basic Usage

```bash
# Place your PDF file as 'payroll.pdf' in the project directory
python main.py
```

### Programmatic Usage

```python
from parsers import PDFParser
from repositories import SQLitePayrollRepository
from exporters import CSVExporter, JSONExporter
from services import PayrollService

# Create service with dependency injection
parser = PDFParser()
repository = SQLitePayrollRepository("payroll.db")
exporters = {
    'csv': CSVExporter(include_summary=True),
    'json': JSONExporter(pretty=True)
}

service = PayrollService(parser, repository, exporters)

# Process payroll
payroll = service.process_payroll("payroll.pdf", save=True)

# Export
service.export_payroll(payroll, 'csv', 'output.csv')
service.export_payroll(payroll, 'json', 'output.json')

# Query
from domain import PayrollPeriod
period = PayrollPeriod(month=9, year=2024)
payroll = service.get_payroll(period)
```

---

## 🎨 Design Patterns Used

### ✅ **SOLID Principles**

#### Single Responsibility

- Each class has one reason to change
- `Money` only handles monetary values
- `Employee` only represents employee data

#### Open/Closed

- Open for extension via interfaces
- Closed for modification
- Add new parsers/exporters without changing existing code

#### Liskov Substitution

- Any `PayrollRepository` can replace another
- Any `PayrollExporter` can replace another
- Polymorphism without side effects

#### Interface Segregation

- Small, focused interfaces
- `PayrollExporter` has single `export()` method
- Clients don't depend on unused methods

#### Dependency Inversion

- High-level modules depend on abstractions
- `PayrollService` depends on `PayrollRepository` interface
- Not on concrete `SQLitePayrollRepository`

### 🔧 **Design Patterns**

1. **Repository Pattern**

   - Abstracts data access
   - `PayrollRepository` interface
   - Multiple implementations possible

2. **Strategy Pattern**

   - `DateParser` uses multiple strategies
   - Each strategy tries different detection methods
   - Priority-based selection

3. **Factory Pattern**

   - `create_payroll_service()` factory function
   - Constructs service with all dependencies

4. **Aggregate Pattern**

   - `Payroll` is aggregate root
   - Manages `Employee` entities
   - Ensures consistency

5. **Value Object Pattern**
   - `Money`, `PayrollPeriod` are immutable
   - Equality by value, not reference

---

## 🧪 Testing Strategy

### Unit Tests

```python
# Test domain entities
def test_money_addition():
    m1 = Money(100)
    m2 = Money(50)
    assert m1 + m2 == Money(150)

# Test parsers with mocks
def test_employee_parser():
    parser = EmployeeParser()
    lines = [TextLine(...), ...]
    employees = parser.parse_employees(lines)
    assert len(employees) > 0
```

### Integration Tests

```python
# Test service with real dependencies
def test_payroll_service_integration():
    service = create_payroll_service(":memory:")
    payroll = service.process_payroll("test.pdf")
    assert payroll.get_employee_count() > 0
```

---

## 📊 Database Schema

```sql
-- Payroll table
CREATE TABLE payroll (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    period_month INTEGER NOT NULL,
    period_year INTEGER NOT NULL,
    total_gross REAL NOT NULL,
    total_net REAL NOT NULL,
    employee_count INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(period_month, period_year)
);

-- Employee table
CREATE TABLE employee (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payroll_id INTEGER NOT NULL,
    employee_id TEXT NOT NULL,
    name TEXT NOT NULL,
    position TEXT NOT NULL,
    gross_value REAL NOT NULL,
    net_value REAL NOT NULL,
    page INTEGER NOT NULL,
    FOREIGN KEY (payroll_id) REFERENCES payroll(id) ON DELETE CASCADE,
    UNIQUE(payroll_id, employee_id)
);
```

---

## 🎯 Benefits of This Architecture

| Benefit             | Description                                       |
| ------------------- | ------------------------------------------------- |
| **Testability**     | Easy to mock dependencies and write unit tests    |
| **Maintainability** | Clear separation makes changes localized          |
| **Extensibility**   | Add new features without modifying existing code  |
| **Flexibility**     | Swap implementations (SQLite → PostgreSQL) easily |
| **Reusability**     | Domain logic independent of infrastructure        |
| **Scalability**     | Easy to add new parsers, exporters, repositories  |

---

## 🔄 Example Output

```
======================================================================
PAYROLLEXTRACT - Smart Payroll Data Extraction
Clean Architecture Implementation
======================================================================

📄 Processing PDF: payroll.pdf
----------------------------------------------------------------------

✅ Extraction completed
   📊 Lines extracted: 1250
   📅 Period detected: September 2024
      Strategy: competencia
      Source: Page 1
   👥 Employees found: 87

======================================================================
💼 PAYROLL SUMMARY
======================================================================
Period:              September 2024
Period Code:         09/2024
Total Employees:     87
With Payment:        85
Without Payment:     2
----------------------------------------------------------------------
Total Gross:         $       523,456.78
Total Net:           $       412,345.67
Total Deductions:    $       111,111.11
----------------------------------------------------------------------
Average Gross:       $         6,016.17
Average Net:         $         4,740.65
======================================================================

📋 Sample Employees (top 5 by gross salary):
----------------------------------------------------------------------

1. JOHN DOE SILVA (ID: 123456)
   Position:    Senior Developer
   Gross:       $ 12,500.00
   Net:         $ 9,800.00
   Deductions:  $ 2,700.00 (21.6%)
   Page:        3

======================================================================
✅ Processing completed successfully!
======================================================================
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-parser`)
3. Follow Clean Architecture principles
4. Write tests
5. Commit changes (`git commit -am 'Add new parser'`)
6. Push to branch (`git push origin feature/new-parser`)
7. Create Pull Request

---

## 📝 License

MIT License - See LICENSE file for details

---

## 🎓 Learn More

- [Clean Architecture by Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Domain-Driven Design](https://en.wikipedia.org/wiki/Domain-driven_design)

---

**PayrollExtract** - Professional payroll processing with Clean Architecture 🏗️✨
