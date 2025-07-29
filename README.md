# Credit Portfolio Analysis

A comprehensive credit portfolio analysis tool that provides detailed insights into loan portfolio performance, customer behavior, and business metrics.

## 📊 Overview

This project analyzes credit portfolio data across two main components:

- **Part 1: Loan Tape Analysis** - Portfolio risk metrics and yield analysis
- **Part 2: Orders Data Analysis** - Customer lifetime value, order patterns, and business metrics

## 🏗️ Project Structure

```
credit-portfolio-analysis/
├── assets/
│   ├── part-1/
│   │   └── test_loan_tape.csv          # Loan portfolio data
│   └── part-2/
│       ├── test_orders.csv              # Order transaction data
│       └── test_bank_transactions.csv   # Banking transaction data
├── src/
│   ├── part_1_loan_tape_analysis/      # Loan portfolio analysis modules
│   ├── part_2_orders_data_analysis/     # Orders and business analysis modules
│   ├── reporting/                       # HTML report generation
│   └── utils/                          # Utility functions
├── reports/                            # Generated HTML reports
├── test/                               # Test files
├── main.py                             # Main execution script
└── requirements.txt                    # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or conda

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/thiebault-husson/credit-portfolio-analysis.git
   cd credit-portfolio-analysis
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the analysis:**
   ```bash
   python main.py
   ```

## 📈 Features

### Part 1: Loan Portfolio Analysis

- **Portfolio Risk Metrics**
  - Delinquency rates by month
  - Default rates and charge-off rates
  - Account status distribution
  - Portfolio-wide risk indicators

- **Portfolio Yield Metrics**
  - Average APR calculations
  - Weighted average APR
  - Total interest revenue
  - Average balance analysis

- **Business-Level Dashboard**
  - Vintage performance analysis
  - Account type distribution
  - Portfolio performance trends

### Part 2: Orders Data Analysis

- **Customer Lifetime Value (LTV)**
  - Cohort-based LTV analysis
  - Average LTV calculations
  - LTV trends over time

- **Average Order Value (AOV)**
  - Cohort-based AOV analysis
  - AOV trends and patterns
  - Revenue optimization insights

- **Customer Acquisition Cost (CAC)**
  - Marketing spend analysis
  - CAC by cohort
  - LTV/CAC ratio analysis

- **Business Performance Metrics**
  - Total revenue and orders
  - Customer count and behavior
  - Revenue concentration analysis

## 📊 Report Generation

The analysis generates comprehensive HTML reports containing:

- **Executive Summary** with key metrics from both parts
- **Interactive visualizations** using Plotly charts
- **Detailed analysis sections** for each component
- **Business insights and recommendations**

### Report Sections

1. **Executive Summary**
   - Revenue Metrics (Part 2)
   - Portfolio Risk Metrics (Part 1)
   - Customer Metrics (Part 2)

2. **Part 1: Loan Tape Analysis**
   - Portfolio risk and yield metrics
   - Business-level dashboard
   - Additional portfolio metrics

3. **Part 2: Orders Data Analysis**
   - LTV and AOV analysis
   - CAC analysis
   - Cohort performance metrics

4. **Lending Decision & Business Performance**
   - Business performance evaluation
   - Lending assessment factors
   - Additional metrics recommendations

## 🔧 Configuration

### Data Files

Place your data files in the `assets/` directory:

- `assets/part-1/test_loan_tape.csv` - Loan portfolio data
- `assets/part-2/test_orders.csv` - Order transaction data
- `assets/part-2/test_bank_transactions.csv` - Banking transaction data

### Command Line Options

```bash
python main.py [OPTIONS]

Options:
  --start-date DATE     Analysis start date (YYYY-MM-DD)
  --end-date DATE       Analysis end date (YYYY-MM-DD)
  --report-date DATE    Report generation date (YYYY-MM-DD)
  --data-dir PATH       Data directory path
  --output-dir PATH     Output directory path
```

## 📋 Data Requirements

### Loan Tape Data (Part 1)
- Account identifiers
- Account status (Current, Delinquent, Default, etc.)
- Balance information
- APR data
- Account types
- Vintage dates

### Orders Data (Part 2)
- Order identifiers
- Customer identifiers
- Order amounts
- Revenue data
- Order dates
- Cohort information

### Bank Transactions Data (Part 2)
- Transaction identifiers
- Marketing spend categories
- Transaction amounts
- Transaction dates

## 🧪 Testing

Run the test suite:

```bash
python -m pytest test/
```

## 📝 Output

The analysis generates:

1. **HTML Reports** in the `reports/` directory
2. **Console output** with summary statistics
3. **Interactive visualizations** embedded in reports

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Thiebault Husson**
- Email: husson.thiebault@gmail.com
- GitHub: [@thiebault-husson](https://github.com/thiebault-husson)

## 🔗 Repository

- **GitHub:** https://github.com/thiebault-husson/credit-portfolio-analysis
- **Branch:** feat/part-1-portfolio-analysis

---

*Generated on: 2025-07-29* 