#!/usr/bin/env python3
"""
Tests for Part A: Portfolio Metrics Analysis
"""

import sys
import os
import traceback

# Add the parent directory to the path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzer import LoanPortfolioAnalyzer
from src.data_processor import LoanDataProcessor


def test_data_processor():
    """Test data processing functionality."""
    print("Testing data processor...")
    
    # Test currency parsing
    assert LoanDataProcessor.parse_currency("$750,000.00") == 750000.0
    assert LoanDataProcessor.parse_currency("$0.00") == 0.0
    assert LoanDataProcessor.parse_currency("") == 0.0
    
    # Test percentage parsing
    assert LoanDataProcessor.parse_percentage("5.09%") == 0.0509
    assert LoanDataProcessor.parse_percentage("0.00%") == 0.0
    assert LoanDataProcessor.parse_percentage("") == 0.0
    
    print("✓ Data processor tests passed")
    return True


def test_analyzer_initialization():
    """Test analyzer initialization."""
    print("Testing analyzer initialization...")
    
    try:
        analyzer = LoanPortfolioAnalyzer("assets/part-1/test_loan_tape.csv")
        assert analyzer.data is not None
        assert len(analyzer.data) > 0
        print(f"✓ Successfully loaded {len(analyzer.data)} records")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize analyzer: {e}")
        return False


def test_portfolio_metrics():
    """Test portfolio metrics calculation."""
    print("Testing portfolio metrics...")
    
    try:
        analyzer = LoanPortfolioAnalyzer("assets/part-1/test_loan_tape.csv")
        metrics = analyzer.get_portfolio_metrics()
        
        assert metrics is not None
        assert len(metrics) > 0
        
        # Check that metrics have required fields
        latest_metrics = metrics[-1]
        required_fields = [
            'total_accounts', 'delinquency_rate', 'default_rate', 
            'charge_off_rate', 'portfolio_size', 'total_revenue',
            'gross_yield', 'net_yield'
        ]
        
        for field in required_fields:
            assert field in latest_metrics, f"Missing field: {field}"
        
        print(f"✓ Portfolio metrics calculated successfully")
        return True
    except Exception as e:
        print(f"✗ Portfolio metrics test failed: {e}")
        return False


def test_business_metrics():
    """Test business metrics calculation."""
    print("Testing business metrics...")
    
    try:
        analyzer = LoanPortfolioAnalyzer("assets/part-1/test_loan_tape.csv")
        metrics = analyzer.get_business_metrics()
        
        assert metrics is not None
        assert not metrics.empty
        
        # Check that metrics have required columns
        required_columns = [
            'businessGuid', 'vintage_month', 'limit', 'average_daily_balance',
            'credit_account_age', 'total_revenue', 'apr', 'borrower_status'
        ]
        
        for col in required_columns:
            assert col in metrics.columns, f"Missing column: {col}"
        
        print(f"✓ Business metrics calculated successfully")
        return True
    except Exception as e:
        print(f"✗ Business metrics test failed: {e}")
        return False


def test_insights():
    """Test insights generation."""
    print("Testing insights generation...")
    
    try:
        analyzer = LoanPortfolioAnalyzer("assets/part-1/test_loan_tape.csv")
        insights = analyzer.get_insights()
        
        assert insights is not None
        
        # Check that insights have required sections
        required_sections = [
            'portfolio_growth', 'account_type_distribution', 
            'status_distribution', 'revenue_analysis', 'risk_analysis'
        ]
        
        for section in required_sections:
            assert section in insights, f"Missing insight section: {section}"
        
        print(f"✓ Insights generated successfully")
        return True
    except Exception as e:
        print(f"✗ Insights test failed: {e}")
        return False


def main():
    """Run all Part A tests."""
    print("=" * 50)
    print("RUNNING PART A TESTS")
    print("=" * 50)
    
    tests = [
        test_data_processor,
        test_analyzer_initialization,
        test_portfolio_metrics,
        test_business_metrics,
        test_insights
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = test()
            if result:
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"PART A TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 50)
    
    if passed == total:
        print("🎉 All Part A tests passed!")
        return 0
    else:
        print("❌ Some Part A tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 