# Credit Portfolio Analysis

A modern Python implementation for comprehensive credit portfolio analysis with modular architecture.

## 🏗️ Architecture

The project follows a clean, modular architecture:

```
credit-portfolio-analysis/
├── main.py                                    # Unified entry point
├── src/
│   ├── part_1_loan_tape_analysis/            # Part 1: Loan Portfolio Analysis
│   │   ├── loan_tape_analyzer.py             # Main analyzer class
│   │   ├── loan_tape_data_processor.py       # Data loading and preprocessing
│   │   └── loan_tape_metrics.py              # Metric calculations
│   ├── part_2_orders_data_analysis/          # Part 2: Orders Data Analysis
│   │   ├── orders_data_analyzer.py           # Main analyzer class
│   │   └── orders_data_processor.py          # Data loading and preprocessing
│   ├── reporting/                             # HTML report generation (future)
│   │   ├── templates/                         # HTML templates
│   │   └── styles/                           # CSS styles
│   └── utils/                                 # Shared utilities
├── test/
│   ├── test_part_a.py                        # Part 1 tests
│   └── test_part_b.py                        # Part 2 tests
├── run_tests.py                               # Test runner
├── requirements.txt
└── README.md
```

## 🚀 Features

### Part 1: Loan Tape Analysis
- **Portfolio Metrics**: Delinquency rate, default rate, charge-off rate, gross/net yield
- **Business Metrics**: Limit, average daily balance, credit account age, revenue, APR
- **Insights**: Portfolio growth trends, risk analysis, revenue analysis

### Part 2: Orders Data Analysis
- **Lifetime Value (LTV)**: By monthly customer cohort
- **Average Order Value (AOV)**: By monthly customer cohort
- **Customer Acquisition Cost (CAC)**: Estimated from marketing spend
- **Insights**: Customer behavior, revenue trends, geographic distribution

## 📦 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd credit-portfolio-analysis
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Command Line Interface

Run the complete analysis (both parts):
```bash
python main.py --part all
```

Run only Part 1 (Loan Tape Analysis):
```bash
python main.py --part 1
```

Run only Part 2 (Orders Data Analysis):
```bash
python main.py --part 2
```

Generate HTML report (future feature):
```bash
python main.py --part all --output html
```

### Programmatic Usage

```python
from main import CreditPortfolioAnalyzer

# Initialize analyzer
analyzer = CreditPortfolioAnalyzer()

# Run complete analysis
results = analyzer.run_complete()

# Run individual parts
part1_results = analyzer.run_part1()
part2_results = analyzer.run_part2()

# Generate HTML report (future)
html_report = analyzer.generate_html_report(results, "complete")
```

## 🧪 Testing

Run all tests:
```bash
python run_tests.py
```

Run individual test suites:
```bash
python test/test_part_a.py  # Part 1 tests
python test/test_part_b.py  # Part 2 tests
```

## 📊 Output Examples

### Part 1: Loan Tape Analysis
```
PART 1: LOAN TAPE ANALYSIS
============================================================

📊 Data Summary:
   Loaded 1,234 records
   Date range: 2023-01-01 to 2023-12-31
   Unique businesses: 567
   Unique accounts: 890

📈 Portfolio Metrics (Latest Month):
   Total Accounts: 890
   Portfolio Size: $12,345,678.90
   Delinquency Rate: 2.34%
   Default Rate: 0.45%
   Charge-off Rate: 0.12%
   Gross Yield: 8.76%
   Net Yield: 3.76%

💡 Key Insights:
   Total Portfolio Size: $12,345,678.90
   Total Businesses: 567
   Delinquency Rate: 2.34%
```

### Part 2: Orders Data Analysis
```
PART 2: ORDERS DATA ANALYSIS
============================================================

📊 Data Summary:
   Loaded 5,678 orders
   Total customers: 1,234
   Date range: 2023-01-01 to 2023-12-31
   Total revenue: $234,567.89
   Average order value: $41.34
   Bank transactions: 890

💰 Lifetime Value (LTV):
   Average LTV: $189.45
   Total customers: 1,234

📦 Average Order Value (AOV):
   Average AOV: $41.34
   Total orders: 5,678

🎯 Customer Acquisition Cost (CAC):
   Estimated CAC: $45.67
   LTV/CAC ratio: 4.15

💡 Key Insights:
   Repeat customer rate: 23.45%
   Average orders per customer: 4.60
```

## 🔧 Development

### Code Style
- **Naming**: snake_case for functions/variables, PascalCase for classes
- **Type Hints**: All functions include type hints
- **Docstrings**: Comprehensive docstrings for all classes and methods
- **Modular Design**: Clear separation of concerns

### Adding New Features
1. Create new modules in appropriate `src/` subdirectories
2. Add corresponding tests in `test/`
3. Update `main.py` if needed
4. Update documentation

## 📈 Future Enhancements

- **HTML Report Generation**: Interactive charts and tables
- **PDF Export**: Professional report generation
- **Data Visualization**: Charts and graphs
- **Real-time Analysis**: Live data processing
- **API Integration**: RESTful API endpoints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License. 