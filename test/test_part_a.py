#!/usr/bin/env python3
"""
Tests for Part A: Portfolio Metrics Analysis
"""

import sys
import os
import traceback

# Add the parent directory to the path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.part_1_loan_tape_analysis.loan_tape_analyzer import LoanPortfolioAnalyzer
from src.part_1_loan_tape_analysis.loan_tape_data_processor import LoanDataProcessor
from src.part_1_loan_tape_analysis.loan_tape_metrics import PortfolioMetricsCalculator, BusinessMetricsCalculator


def test_data_parsing():
    """Test data parsing functionality."""
    try:
        # Test currency parsing
        assert LoanDataProcessor.parse_currency("$1,234.56") == 1234.56
        assert LoanDataProcessor.parse_currency("$0.00") == 0.0
        assert LoanDataProcessor.parse_currency("$1,000,000.00") == 1000000.0
        
        # Test percentage parsing
        assert LoanDataProcessor.parse_percentage("12.34%") == 0.1234
        assert LoanDataProcessor.parse_percentage("0.00%") == 0.0
        assert LoanDataProcessor.parse_percentage("100.00%") == 1.0
        
        print("✓ Data parsing tests passed")
        return True
    except Exception as e:
        print(f"✗ Data parsing tests failed: {e}")
        traceback.print_exc()
        return False


def test_analyzer_initialization():
    """Test analyzer initialization."""
    try:
        analyzer = LoanPortfolioAnalyzer("assets/part-1/test_loan_tape.csv")
        assert analyzer is not None
        assert analyzer.data is not None
        assert len(analyzer.data) > 0
        
        print("✓ Analyzer initialization tests passed")
        return True
    except Exception as e:
        print(f"✗ Analyzer initialization tests failed: {e}")
        traceback.print_exc()
        return False


def test_portfolio_metrics():
    """Test portfolio metrics calculation."""
    try:
        analyzer = LoanPortfolioAnalyzer("assets/part-1/test_loan_tape.csv")
        metrics = analyzer.get_portfolio_metrics()
        
        assert metrics is not None
        assert len(metrics) > 0
        
        # Check that metrics have required fields
        latest_metrics = metrics[-1]
        required_fields = ['month', 'total_accounts', 'portfolio_size', 'delinquency_rate']
        for field in required_fields:
            assert field in latest_metrics
        
        print("✓ Portfolio metrics tests passed")
        return True
    except Exception as e:
        print(f"✗ Portfolio metrics tests failed: {e}")
        traceback.print_exc()
        return False


def test_business_metrics():
    """Test business metrics calculation."""
    try:
        analyzer = LoanPortfolioAnalyzer("assets/part-1/test_loan_tape.csv")
        metrics = analyzer.get_business_metrics()
        
        assert metrics is not None
        assert len(metrics) > 0
        
        print("✓ Business metrics tests passed")
        return True
    except Exception as e:
        print(f"✗ Business metrics tests failed: {e}")
        traceback.print_exc()
        return False


def test_insights():
    """Test insights generation."""
    try:
        analyzer = LoanPortfolioAnalyzer("assets/part-1/test_loan_tape.csv")
        insights = analyzer.get_insights()
        
        assert insights is not None
        assert 'portfolio_growth' in insights
        assert 'risk_analysis' in insights
        
        print("✓ Insights tests passed")
        return True
    except Exception as e:
        print(f"✗ Insights tests failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all Part A tests."""
    print("=" * 60)
    print("PART A TESTS - LOAN TAPE ANALYSIS")
    print("=" * 60)
    
    tests = [
        test_data_parsing,
        test_analyzer_initialization,
        test_portfolio_metrics,
        test_business_metrics,
        test_insights
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 