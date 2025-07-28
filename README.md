# Credit Portfolio Analysis

A modern Python implementation for credit portfolio analysis with modular architecture.

## Overview

This project implements comprehensive credit portfolio analysis with the following capabilities:

- **Portfolio Metrics**: Delinquency rate, default rate, charge-off rate, gross/net portfolio yield
- **Business Metrics**: Per-business performance by monthly vintage
- **Insights**: Discover patterns and trends from loan portfolio data

## Architecture

The project follows a clean, modular architecture:

```
credit-portfolio-analysis/
├── src/
│   ├── analyzer.py              # Main analysis class
│   ├── data_processor.py        # Data loading and preprocessing
│   └── metrics.py               # Metric calculations
├── test/
│   └── test_part_a.py           # Part A tests
├── main.py                      # Entry point
├── run_tests.py                 # Test runner
├── requirements.txt
└── README.md
```

## Key Classes

### LoanPortfolioAnalyzer
Main class that orchestrates the analysis:
- Loads and preprocesses loan tape data
- Calculates portfolio metrics by month
- Calculates business metrics by vintage
- Generates insights and patterns

### LoanDataProcessor
Handles data loading and preprocessing:
- Parses currency strings (`$750,000.00` → `750000.0`)
- Parses percentage strings (`5.09%` → `0.0509`)
- Converts dates and handles missing values

### PortfolioMetricsCalculator & BusinessMetricsCalculator
Calculate the required metrics:
- Portfolio-level metrics (delinquency, default, charge-off rates)
- Business-level metrics (limit, balance, age, revenue, APR, status)

## Usage

### Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the analysis**:
   ```bash
   python main.py
   ```

3. **Run tests**:
   ```bash
   python run_tests.py
   ```

### Programmatic Usage

```python
from src.analyzer import LoanPortfolioAnalyzer

# Initialize analyzer
analyzer = LoanPortfolioAnalyzer("assets/part-1/test_loan_tape.csv")

# Run complete analysis
results = analyzer.analyze_portfolio()

# Get specific metrics
portfolio_metrics = analyzer.get_portfolio_metrics()
business_metrics = analyzer.get_business_metrics()
insights = analyzer.get_insights()
```

## Output

The analysis produces:

### Portfolio Metrics by Month
- Delinquency rate
- Default rate
- Charge-off rate
- Gross portfolio yield
- Net portfolio yield (SOFR + 5% cost of capital)
- Portfolio size and revenue

### Business Metrics by Vintage
- Limit and average daily balance
- Credit account age
- Revenue (interest + interchange)
- APR and borrower status
- Payment rate

### Key Insights
- Portfolio growth trends
- Account type distribution
- Status distribution
- Revenue analysis
- Risk analysis

## Data Processing

The implementation handles the loan tape data format:
- **Currency parsing**: `$750,000.00` → `750000.0`
- **Percentage parsing**: `5.09%` → `0.0509`
- **Date handling**: Proper datetime conversion
- **Missing values**: Graceful handling of empty fields

## Testing

The project includes organized test suites:

### Part A Tests (`test/test_part_a.py`)
- Data processing functionality
- Analyzer initialization
- Portfolio metrics calculation
- Business metrics calculation
- Insights generation

Run all tests:
```bash
python run_tests.py
```

Run specific test suite:
```bash
python test/test_part_a.py
```

## Requirements

- Python 3.9+
- pandas >= 2.0.0
- numpy >= 1.24.0
- python-dateutil >= 2.8.0

## Design Decisions

1. **Clean Architecture**: Simple, focused classes with clear responsibilities
2. **Type Hints**: Comprehensive typing for better code quality
3. **Error Handling**: Graceful handling of data issues
4. **Modularity**: Easy to extend with new metrics or insights
5. **Testability**: Well-structured for unit testing

## Next Steps

This implementation provides a solid foundation for:
- Adding additional data sources
- Implementing visualizations
- Adding more sophisticated metrics
- Creating comprehensive reports 