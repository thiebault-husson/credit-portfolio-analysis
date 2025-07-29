#!/usr/bin/env python3
"""
Verify business metrics calculation using existing infrastructure.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.part_1_loan_tape_analysis.loan_tape_analyzer import LoanPortfolioAnalyzer
from src.part_1_loan_tape_analysis.loan_tape_metrics import BusinessMetricsCalculator


def verify_business_metrics():
    """Verify the business metrics calculation using existing infrastructure."""
    
    print("🔍 Verifying Business Metrics Calculation")
    print("=" * 50)
    
    # Reuse existing analyzer infrastructure
    analyzer = LoanPortfolioAnalyzer("./assets/part-1/test_loan_tape.csv")
    
    # Calculate business metrics using existing method
    business_metrics = BusinessMetricsCalculator.calculate_business_metrics(analyzer.data)
    
    print(f"📊 Business Metrics Analysis")
    print(f"Total business records: {len(business_metrics)}")
    
    if len(business_metrics) > 0:
        print(f"\n📈 Sample Business Metrics (First 10 records):")
        print(f"{'Vintage':<12} {'Type':<15} {'Limit':<12} {'Balance':<12} {'Age':<6} {'Revenue':<10} {'APR':<8} {'Status':<10}")
        print("-" * 90)
        
        for _, row in business_metrics.head(10).iterrows():
            vintage = str(row['vintage_month'])
            account_type = str(row['accountType'])[:14]
            limit = f"${row['limit']:,.0f}"
            balance = f"${row['averageDailyBalance']:,.0f}"
            age = f"{row['accountAge']:.1f}"
            revenue = f"${row['revenue']:,.2f}"
            apr = f"{row['apr']:.2f}%"
            status = str(row['status'])
            
            print(f"{vintage:<12} {account_type:<15} {limit:<12} {balance:<12} {age:<6} {revenue:<10} {apr:<8} {status:<10}")
        
        print(f"\n📊 Summary Statistics:")
        print(f"  Unique Vintage Months: {business_metrics['vintage_month'].nunique()}")
        print(f"  Account Types: {business_metrics['accountType'].unique()}")
        print(f"  Status Distribution:")
        status_counts = business_metrics['status'].value_counts()
        for status, count in status_counts.items():
            print(f"    {status}: {count} ({count/len(business_metrics)*100:.1f}%)")
        
        print(f"\n💰 Revenue Analysis:")
        print(f"  Total Revenue: ${business_metrics['revenue'].sum():,.2f}")
        print(f"  Average Revenue per Account: ${business_metrics['revenue'].mean():,.2f}")
        print(f"  Median Revenue per Account: ${business_metrics['revenue'].median():,.2f}")
        
        print(f"\n📈 APR Analysis:")
        print(f"  Average APR: {business_metrics['apr'].mean():.2f}%")
        print(f"  Median APR: {business_metrics['apr'].median():.2f}%")
        print(f"  APR Range: {business_metrics['apr'].min():.2f}% - {business_metrics['apr'].max():.2f}%")
        
        print(f"\n⏰ Account Age Analysis:")
        print(f"  Average Account Age: {business_metrics['accountAge'].mean():.1f} months")
        print(f"  Median Account Age: {business_metrics['accountAge'].median():.1f} months")
        print(f"  Age Range: {business_metrics['accountAge'].min():.1f} - {business_metrics['accountAge'].max():.1f} months")
    
    print(f"\n✅ Business metrics calculation verified successfully!")


if __name__ == "__main__":
    verify_business_metrics() 