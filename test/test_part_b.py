#!/usr/bin/env python3
"""
Tests for Part B: Orders Analysis
"""

import sys
import os
import traceback
import pandas as pd

# Add the parent directory to the path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.part_2_orders_data_analysis.orders_data_analyzer import OrdersAnalyzer
from src.part_2_orders_data_analysis.orders_data_processor import OrdersDataProcessor

# Global analyzer instance to avoid redundant data processing
_analyzer = None

def get_analyzer():
    """Get or create a shared analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = OrdersAnalyzer(
            "assets/part-2/test_orders.csv",
            "assets/part-2/test_bank_transactions.csv"
        )
    return _analyzer

def test_data_loading():
    """Test data loading functionality."""
    try:
        # Test orders data loading
        orders_data = OrdersDataProcessor.load_orders_data("assets/part-2/test_orders.csv")
        assert orders_data is not None
        assert len(orders_data) > 0
        
        # Test bank transactions loading
        bank_data = OrdersDataProcessor.load_bank_transactions("assets/part-2/test_bank_transactions.csv")
        assert bank_data is not None
        assert len(bank_data) > 0
        
        print("✓ Data loading tests passed")
        return True
    except Exception as e:
        print(f"✗ Data loading tests failed: {e}")
        traceback.print_exc()
        return False


def test_analyzer_initialization():
    """Test analyzer initialization."""
    try:
        analyzer = get_analyzer()
        assert analyzer is not None
        assert analyzer.orders_data is not None
        assert analyzer.bank_transactions is not None
        
        print("✓ Analyzer initialization tests passed")
        return True
    except Exception as e:
        print(f"✗ Analyzer initialization tests failed: {e}")
        traceback.print_exc()
        return False


def test_lifetime_value():
    """Test lifetime value calculation."""
    try:
        analyzer = get_analyzer()
        ltv_analysis = analyzer._calculate_cohort_ltv()
        
        assert ltv_analysis is not None
        assert 'by_cohort' in ltv_analysis
        assert 'summary' in ltv_analysis
        
        summary = ltv_analysis['summary']
        assert 'average_ltv' in summary
        assert 'total_customers' in summary
        
        print("✓ Lifetime value tests passed")
        return True
    except Exception as e:
        print(f"✗ Lifetime value tests failed: {e}")
        traceback.print_exc()
        return False


def test_average_order_value():
    """Test average order value calculation."""
    try:
        analyzer = get_analyzer()
        aov_analysis = analyzer._calculate_cohort_aov()
        
        assert aov_analysis is not None
        assert 'by_cohort' in aov_analysis
        assert 'summary' in aov_analysis
        
        summary = aov_analysis['summary']
        assert 'average_aov' in summary
        assert 'total_orders' in summary
        
        print("✓ Average order value tests passed")
        return True
    except Exception as e:
        print(f"✗ Average order value tests failed: {e}")
        traceback.print_exc()
        return False


def test_customer_acquisition_cost():
    """Test customer acquisition cost calculation."""
    try:
        analyzer = get_analyzer()
        cac_analysis = analyzer._calculate_cohort_cac()
        
        assert cac_analysis is not None
        assert 'by_cohort' in cac_analysis
        assert 'summary' in cac_analysis
        
        summary = cac_analysis['summary']
        assert 'estimated_cac' in summary
        assert 'ltv_cac_ratio' in summary
        
        print("✓ Customer acquisition cost tests passed")
        return True
    except Exception as e:
        print(f"✗ Customer acquisition cost tests failed: {e}")
        traceback.print_exc()
        return False


def test_insights():
    """Test insights generation."""
    try:
        analyzer = get_analyzer()
        insights = analyzer._generate_insights()
        
        assert insights is not None
        assert 'customer_behavior' in insights
        assert 'revenue_trends' in insights
        
        behavior = insights['customer_behavior']
        assert 'total_customers' in behavior
        assert 'repeat_customer_rate' in behavior
        
        print("✓ Insights tests passed")
        return True
    except Exception as e:
        print(f"✗ Insights tests failed: {e}")
        traceback.print_exc()
        return False


def test_discount_logic():
    """Test discount and refund logic."""
    try:
        # Test with sample data to avoid loading full dataset again
        processor = OrdersDataProcessor()
        
        # Create a small test dataset
        test_orders = pd.DataFrame({
            'customer': ['A', 'B', 'C'],
            'line_items': [
                '[{"price_set": {"shop_amount": "100.00"}}]',
                '[{"price_set": {"shop_amount": "200.00"}}]',
                '[{"price_set": {"shop_amount": "150.00"}}]'
            ],
            'refunds': [
                '{"shop_amount": "10.00"}',
                '{"presentment_amount": "20.00"}',
                '0'
            ],
            'discounts': [
                '{"amount": "5.00"}',
                '{"amount": "15.00"}',
                '0'
            ],
            'created_at': ['2024-01-01', '2024-01-02', '2024-01-03']
        })
        
        # Test the processing logic
        test_orders['gross_amount'] = test_orders['line_items'].apply(processor._extract_total_amount)
        test_orders['refunds'] = test_orders['refunds'].apply(processor._parse_refunds)
        test_orders['discounts'] = test_orders['discounts'].apply(processor._parse_discounts)
        test_orders['net_revenue'] = test_orders['gross_amount'] - test_orders['refunds'] - test_orders['discounts']
        
        # Verify calculations
        assert test_orders['gross_amount'].sum() == 450.0
        assert test_orders['refunds'].sum() == 30.0
        assert test_orders['discounts'].sum() == 20.0
        assert test_orders['net_revenue'].sum() == 400.0
        
        print("✓ Discount logic tests passed")
        return True
    except Exception as e:
        print(f"✗ Discount logic tests failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("PART B TESTS - ORDERS DATA ANALYSIS")
    print("=" * 60)
    
    tests = [
        test_data_loading,
        test_analyzer_initialization,
        test_lifetime_value,
        test_average_order_value,
        test_customer_acquisition_cost,
        test_insights,
        test_discount_logic
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("✅ Part B tests completed successfully")
    else:
        print("❌ Part B tests failed")


if __name__ == "__main__":
    main() 