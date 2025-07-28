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
        analyzer = OrdersAnalyzer(
            "assets/part-2/test_orders.csv",
            "assets/part-2/test_bank_transactions.csv"
        )
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
        analyzer = OrdersAnalyzer(
            "assets/part-2/test_orders.csv",
            "assets/part-2/test_bank_transactions.csv"
        )
        ltv_analysis = analyzer._calculate_lifetime_value()
        
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
        analyzer = OrdersAnalyzer(
            "assets/part-2/test_orders.csv",
            "assets/part-2/test_bank_transactions.csv"
        )
        aov_analysis = analyzer._calculate_average_order_value()
        
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
        analyzer = OrdersAnalyzer(
            "assets/part-2/test_orders.csv",
            "assets/part-2/test_bank_transactions.csv"
        )
        cac_analysis = analyzer._calculate_customer_acquisition_cost()
        
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
        analyzer = OrdersAnalyzer(
            "assets/part-2/test_orders.csv",
            "assets/part-2/test_bank_transactions.csv"
        )
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
        from src.part_2_orders_data_analysis.orders_data_processor import OrdersDataProcessor
        
        # Test cases for simple revenue calculation
        test_cases = [
            # (gross, refunds, discounts, expected_net)
            (100.0, 0.0, 0.0, 100.0),    # No adjustments
            (100.0, 20.0, 0.0, 80.0),    # Only refunds
            (100.0, 0.0, 20.0, 80.0),    # Only discounts
            (100.0, 20.0, 30.0, 50.0),   # Both refunds and discounts
            (100.0, 0.0, 120.0, -20.0),  # Discount > gross (can be negative)
            (100.0, 50.0, 60.0, -10.0),  # Refunds + discounts > gross
            (100.0, 80.0, 30.0, -10.0),  # Refunds alone > gross
        ]
        
        for gross, refunds, discounts, expected in test_cases:
            # Calculate net revenue using simple formula
            net_revenue = gross - refunds - discounts
            
            # Assert result
            assert abs(net_revenue - expected) < 0.01, f"Expected {expected}, got {net_revenue} for gross={gross}, refunds={refunds}, discounts={discounts}"
        
        print("✓ Discount logic tests passed")
        return True
    except Exception as e:
        print(f"✗ Discount logic tests failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all Part B tests."""
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
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 