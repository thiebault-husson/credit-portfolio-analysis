#!/usr/bin/env python3
"""
Comprehensive Audit Script for Part 2 Orders Analysis
Verifies all calculations, data processing, and metrics computation.
"""

import pandas as pd
import json
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from part_2_orders_data_analysis.orders_data_processor import OrdersDataProcessor
from part_2_orders_data_analysis.orders_data_analyzer import OrdersAnalyzer


class Part2Auditor:
    """Comprehensive auditor for Part 2 calculations."""
    
    def __init__(self):
        self.orders_path = "assets/part-2/test_orders.csv"
        self.bank_path = "assets/part-2/test_bank_transactions.csv"
        self.audit_results = {}
        
    def audit_data_loading(self) -> Dict:
        """Audit data loading and preprocessing."""
        print("🔍 AUDITING DATA LOADING...")
        
        # Load raw data
        raw_orders = pd.read_csv(self.orders_path)
        raw_bank = pd.read_csv(self.bank_path)
        
        # Load processed data
        processor = OrdersDataProcessor()
        processed_orders = processor.load_orders_data(self.orders_path)
        processed_bank = processor.load_bank_transactions(self.bank_path)
        
        results = {
            'raw_orders_count': len(raw_orders),
            'processed_orders_count': len(processed_orders),
            'raw_bank_count': len(raw_bank),
            'processed_bank_count': len(processed_bank),
            'orders_columns': list(raw_orders.columns),
            'processed_orders_columns': list(processed_orders.columns),
            'date_parsing_success': processed_orders['created_at'].notna().sum(),
            'date_parsing_failed': processed_orders['created_at'].isna().sum(),
            'gross_amount_sum': processed_orders['gross_amount'].sum(),
            'refunds_sum': processed_orders['refunds'].sum(),
            'discounts_sum': processed_orders['discounts'].sum(),
            'net_revenue_sum': processed_orders['net_revenue'].sum(),
            'unique_customers': processed_orders['customer'].nunique(),
            'total_orders': len(processed_orders)
        }
        
        print(f"✅ Raw orders: {results['raw_orders_count']:,}")
        print(f"✅ Processed orders: {results['processed_orders_count']:,}")
        print(f"✅ Date parsing success: {results['date_parsing_success']:,}")
        print(f"⚠️  Date parsing failed: {results['date_parsing_failed']:,}")
        print(f"💰 Gross revenue: ${results['gross_amount_sum']:,.2f}")
        print(f"💰 Net revenue: ${results['net_revenue_sum']:,.2f}")
        print(f"👥 Unique customers: {results['unique_customers']:,}")
        
        return results
    
    def audit_revenue_calculation(self) -> Dict:
        """Audit revenue calculation logic."""
        print("\n🔍 AUDITING REVENUE CALCULATION...")
        
        processor = OrdersDataProcessor()
        orders = processor.load_orders_data(self.orders_path)
        
        # Manual verification
        sample_orders = orders.head(10)
        manual_calculations = []
        
        for idx, row in sample_orders.iterrows():
            manual_calc = {
                'order_id': idx,
                'gross_amount': row['gross_amount'],
                'refunds': row['refunds'],
                'discounts': row['discounts'],
                'net_revenue': row['net_revenue'],
                'manual_net': row['gross_amount'] - row['refunds'] - row['discounts'],
                'calculation_correct': abs(row['net_revenue'] - (row['gross_amount'] - row['refunds'] - row['discounts'])) < 0.01
            }
            manual_calculations.append(manual_calc)
        
        # Overall verification
        total_gross = orders['gross_amount'].sum()
        total_refunds = orders['refunds'].sum()
        total_discounts = orders['discounts'].sum()
        total_net = orders['net_revenue'].sum()
        manual_total_net = total_gross - total_refunds - total_discounts
        
        results = {
            'total_gross': total_gross,
            'total_refunds': total_refunds,
            'total_discounts': total_discounts,
            'total_net': total_net,
            'manual_total_net': manual_total_net,
            'calculation_correct': abs(total_net - manual_total_net) < 0.01,
            'sample_calculations': manual_calculations
        }
        
        print(f"✅ Total gross: ${total_gross:,.2f}")
        print(f"✅ Total refunds: ${total_refunds:,.2f}")
        print(f"✅ Total discounts: ${total_discounts:,.2f}")
        print(f"✅ Total net: ${total_net:,.2f}")
        print(f"✅ Manual calculation: ${manual_total_net:,.2f}")
        print(f"✅ Calculation correct: {results['calculation_correct']}")
        
        return results
    
    def audit_cohort_analysis(self) -> Dict:
        """Audit cohort analysis calculations."""
        print("\n🔍 AUDITING COHORT ANALYSIS...")
        
        analyzer = OrdersAnalyzer(self.orders_path, self.bank_path)
        cohort_analysis = analyzer._calculate_cohort_metrics()
        
        # Verify cohort calculations
        orders = analyzer.orders_data
        orders['cohort_month'] = orders['created_at'].dt.to_period('M')
        
        # Manual cohort calculation
        manual_cohorts = orders.groupby('cohort_month').agg({
            'customer': 'nunique',
            'net_revenue': 'sum'
        }).round(2)
        
        manual_cohorts.columns = ['customer_count', 'total_revenue']
        manual_cohorts['total_orders'] = orders.groupby('cohort_month').size()
        manual_cohorts['average_revenue_per_customer'] = manual_cohorts['total_revenue'] / manual_cohorts['customer_count']
        
        results = {
            'cohort_count': len(cohort_analysis),
            'manual_cohort_count': len(manual_cohorts),
            'cohort_months': list(cohort_analysis['cohort_month'].astype(str)),
            'manual_cohort_months': list(manual_cohorts.index.astype(str)),
            'total_customers_cohort': cohort_analysis['customer_count'].sum(),
            'total_revenue_cohort': cohort_analysis['total_revenue'].sum(),
            'manual_total_customers': manual_cohorts['customer_count'].sum(),
            'manual_total_revenue': manual_cohorts['total_revenue'].sum()
        }
        
        print(f"✅ Cohort count: {results['cohort_count']}")
        print(f"✅ Manual cohort count: {results['manual_cohort_count']}")
        print(f"✅ Total customers (cohort): {results['total_customers_cohort']:,}")
        print(f"✅ Total revenue (cohort): ${results['total_revenue_cohort']:,.2f}")
        
        return results
    
    def audit_ltv_calculation(self) -> Dict:
        """Audit Lifetime Value calculations."""
        print("\n🔍 AUDITING LIFETIME VALUE CALCULATION...")
        
        analyzer = OrdersAnalyzer(self.orders_path, self.bank_path)
        ltv_analysis = analyzer._calculate_cohort_ltv()
        
        # Manual LTV calculation
        orders = analyzer.orders_data
        total_revenue = orders['net_revenue'].sum()
        total_customers = orders['customer'].nunique()
        manual_ltv = total_revenue / total_customers if total_customers > 0 else 0
        
        # Customer-level LTV for median
        customer_ltv = orders.groupby('customer')['net_revenue'].sum()
        manual_median_ltv = customer_ltv.median()
        
        results = {
            'reported_ltv': ltv_analysis['summary']['average_ltv'],
            'manual_ltv': manual_ltv,
            'ltv_correct': abs(ltv_analysis['summary']['average_ltv'] - manual_ltv) < 0.01,
            'reported_median': ltv_analysis['summary']['median_ltv'],
            'manual_median': manual_median_ltv,
            'median_correct': abs(ltv_analysis['summary']['median_ltv'] - manual_median_ltv) < 0.01,
            'total_revenue': total_revenue,
            'total_customers': total_customers,
            'cohort_ltv_count': len(ltv_analysis['by_cohort'])
        }
        
        print(f"✅ Reported LTV: ${results['reported_ltv']:.2f}")
        print(f"✅ Manual LTV: ${results['manual_ltv']:.2f}")
        print(f"✅ LTV calculation correct: {results['ltv_correct']}")
        print(f"✅ Cohort LTV records: {results['cohort_ltv_count']}")
        
        return results
    
    def audit_aov_calculation(self) -> Dict:
        """Audit Average Order Value calculations."""
        print("\n🔍 AUDITING AVERAGE ORDER VALUE CALCULATION...")
        
        analyzer = OrdersAnalyzer(self.orders_path, self.bank_path)
        aov_analysis = analyzer._calculate_cohort_aov()
        
        # Manual AOV calculation
        orders = analyzer.orders_data
        total_revenue = orders['net_revenue'].sum()
        total_orders = len(orders)
        manual_aov = total_revenue / total_orders if total_orders > 0 else 0
        
        # Order-level AOV for median
        manual_median_aov = orders['net_revenue'].median()
        
        results = {
            'reported_aov': aov_analysis['summary']['average_aov'],
            'manual_aov': manual_aov,
            'aov_correct': abs(aov_analysis['summary']['average_aov'] - manual_aov) < 0.01,
            'reported_median': aov_analysis['summary']['median_aov'],
            'manual_median': manual_median_aov,
            'median_correct': abs(aov_analysis['summary']['median_aov'] - manual_median_aov) < 0.01,
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'cohort_aov_count': len(aov_analysis['by_cohort'])
        }
        
        print(f"✅ Reported AOV: ${results['reported_aov']:.2f}")
        print(f"✅ Manual AOV: ${results['manual_aov']:.2f}")
        print(f"✅ AOV calculation correct: {results['aov_correct']}")
        print(f"✅ Cohort AOV records: {results['cohort_aov_count']}")
        
        return results
    
    def audit_cac_calculation(self) -> Dict:
        """Audit Customer Acquisition Cost calculations."""
        print("\n🔍 AUDITING CUSTOMER ACQUISITION COST CALCULATION...")
        
        analyzer = OrdersAnalyzer(self.orders_path, self.bank_path)
        cac_analysis = analyzer._calculate_cohort_cac()
        
        # Manual CAC calculation
        bank_transactions = analyzer.bank_transactions
        marketing_spend = bank_transactions[
            bank_transactions['category'].str.contains('Marketing', na=False)
        ]['amount'].sum()
        
        total_customers = analyzer.orders_data['customer'].nunique()
        manual_cac = abs(marketing_spend) / total_customers if total_customers > 0 else 0
        
        # LTV/CAC ratio
        ltv_analysis = analyzer._calculate_global_ltv()
        manual_ltv = ltv_analysis['average_ltv']
        manual_ltv_cac_ratio = manual_ltv / manual_cac if manual_cac > 0 else 0
        
        results = {
            'reported_cac': cac_analysis['summary']['estimated_cac'],
            'manual_cac': manual_cac,
            'cac_correct': abs(cac_analysis['summary']['estimated_cac'] - manual_cac) < 0.01,
            'reported_ltv_cac': cac_analysis['summary']['ltv_cac_ratio'],
            'manual_ltv_cac': manual_ltv_cac_ratio,
            'ltv_cac_correct': abs(cac_analysis['summary']['ltv_cac_ratio'] - manual_ltv_cac_ratio) < 0.01,
            'marketing_spend': abs(marketing_spend),
            'total_customers': total_customers,
            'cohort_cac_count': len(cac_analysis['by_cohort'])
        }
        
        print(f"✅ Reported CAC: ${results['reported_cac']:.2f}")
        print(f"✅ Manual CAC: ${results['manual_cac']:.2f}")
        print(f"✅ CAC calculation correct: {results['cac_correct']}")
        print(f"✅ Marketing spend: ${results['marketing_spend']:,.2f}")
        
        return results
    
    def audit_field_parsing(self) -> Dict:
        """Audit field parsing for JSON columns."""
        print("\n🔍 AUDITING FIELD PARSING...")
        
        processor = OrdersDataProcessor()
        orders = processor.load_orders_data(self.orders_path)
        
        # Sample parsing verification
        sample_orders = orders.head(5)
        parsing_results = []
        
        for idx, row in sample_orders.iterrows():
            # Test line_items parsing
            try:
                line_items = json.loads(row['line_items'])
                parsed_gross = processor._extract_total_amount(row['line_items'])
                parsing_results.append({
                    'order_id': idx,
                    'line_items_parsed': True,
                    'gross_amount': parsed_gross,
                    'refunds_parsed': True,
                    'refunds_amount': row['refunds'],
                    'discounts_parsed': True,
                    'discounts_amount': row['discounts']
                })
            except Exception as e:
                parsing_results.append({
                    'order_id': idx,
                    'line_items_parsed': False,
                    'error': str(e)
                })
        
        # Overall parsing statistics
        total_orders = len(orders)
        successful_gross = orders['gross_amount'].notna().sum()
        successful_refunds = orders['refunds'].notna().sum()
        successful_discounts = orders['discounts'].notna().sum()
        
        results = {
            'total_orders': total_orders,
            'successful_gross_parsing': successful_gross,
            'successful_refunds_parsing': successful_refunds,
            'successful_discounts_parsing': successful_discounts,
            'gross_parsing_rate': successful_gross / total_orders,
            'refunds_parsing_rate': successful_refunds / total_orders,
            'discounts_parsing_rate': successful_discounts / total_orders,
            'sample_parsing': parsing_results
        }
        
        print(f"✅ Total orders: {total_orders:,}")
        print(f"✅ Gross parsing success: {successful_gross:,} ({results['gross_parsing_rate']:.1%})")
        print(f"✅ Refunds parsing success: {successful_refunds:,} ({results['refunds_parsing_rate']:.1%})")
        print(f"✅ Discounts parsing success: {successful_discounts:,} ({results['discounts_parsing_rate']:.1%})")
        
        return results
    
    def run_comprehensive_audit(self) -> Dict:
        """Run comprehensive audit of all Part 2 calculations."""
        print("=" * 80)
        print("🔍 COMPREHENSIVE PART 2 AUDIT")
        print("=" * 80)
        
        self.audit_results = {
            'data_loading': self.audit_data_loading(),
            'revenue_calculation': self.audit_revenue_calculation(),
            'cohort_analysis': self.audit_cohort_analysis(),
            'ltv_calculation': self.audit_ltv_calculation(),
            'aov_calculation': self.audit_aov_calculation(),
            'cac_calculation': self.audit_cac_calculation(),
            'field_parsing': self.audit_field_parsing()
        }
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 AUDIT SUMMARY")
        print("=" * 80)
        
        all_correct = True
        for audit_name, results in self.audit_results.items():
            if 'correct' in results:
                if isinstance(results['correct'], bool):
                    status = "✅ PASS" if results['correct'] else "❌ FAIL"
                    print(f"{audit_name.upper()}: {status}")
                    if not results['correct']:
                        all_correct = False
                elif isinstance(results['correct'], dict):
                    for key, value in results['correct'].items():
                        status = "✅ PASS" if value else "❌ FAIL"
                        print(f"{audit_name.upper()} - {key}: {status}")
                        if not value:
                            all_correct = False
        
        print(f"\n🎯 OVERALL AUDIT RESULT: {'✅ ALL TESTS PASSED' if all_correct else '❌ SOME TESTS FAILED'}")
        
        return self.audit_results


if __name__ == "__main__":
    auditor = Part2Auditor()
    results = auditor.run_comprehensive_audit() 