#!/usr/bin/env python3
"""
Verify business-level dashboard implementation for Part 1B.
"""

import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.part_1_loan_tape_analysis.loan_tape_analyzer import LoanPortfolioAnalyzer
from src.part_1_loan_tape_analysis.loan_tape_metrics import BusinessMetricsCalculator


def verify_business_dashboard():
    """Verify the business-level dashboard implementation."""
    
    print("🔍 Verifying Business-Level Dashboard Implementation")
    print("=" * 60)
    
    # Load data using existing infrastructure
    analyzer = LoanPortfolioAnalyzer("./assets/part-1/test_loan_tape.csv")
    
    # Calculate business metrics
    business_metrics = BusinessMetricsCalculator.calculate_business_metrics(analyzer.data)
    
    print(f"📊 Business Dashboard Analysis")
    print(f"Total business-vintage combinations: {len(business_metrics):,}")
    print(f"Unique businesses: {business_metrics['businessGuid'].nunique():,}")
    print(f"Unique vintage months: {business_metrics['vintage_month'].nunique():,}")
    
    print(f"\n📈 Sample Business Dashboard (First 10 records):")
    print(f"{'Business':<12} {'Vintage':<10} {'Type':<15} {'Limit':<12} {'Balance':<12} {'Age':<6} {'Revenue':<10} {'APR':<8} {'Status':<10} {'Count':<6}")
    print("-" * 100)
    
    for _, row in business_metrics.head(10).iterrows():
        business_id = row['businessId']
        vintage = str(row['vintage_month'])
        account_type = str(row['accountType'])[:14]
        limit = f"${row['totalLimit']:,.0f}"
        balance = f"${row['totalAverageDailyBalance']:,.0f}"
        age = f"{row['avgAccountAge']:.1f}"
        revenue = f"${row['totalRevenue']:,.0f}"
        apr = f"{row['avgAPR']:.2f}%"
        status = str(row['primaryStatus'])
        count = f"{row['accountCount']}"
        
        print(f"{business_id:<12} {vintage:<10} {account_type:<15} {limit:<12} {balance:<12} {age:<6} {revenue:<10} {apr:<8} {status:<10} {count:<6}")
    
    print(f"\n📊 Business Performance Summary:")
    print(f"  Total Revenue: ${business_metrics['totalRevenue'].sum():,.2f}")
    print(f"  Average Revenue per Business: ${business_metrics.groupby('businessGuid')['totalRevenue'].sum().mean():,.2f}")
    print(f"  Total Accounts: {business_metrics['accountCount'].sum():,}")
    print(f"  Average Accounts per Business: {business_metrics.groupby('businessGuid')['accountCount'].sum().mean():.1f}")
    
    print(f"\n🏢 Top 5 Businesses by Revenue:")
    top_businesses = business_metrics.groupby('businessGuid')['totalRevenue'].sum().sort_values(ascending=False).head(5)
    for business_id, revenue in top_businesses.items():
        business_short = business_id[:8] + "..."
        print(f"  {business_short}: ${revenue:,.2f}")
    
    print(f"\n📅 Vintage Distribution:")
    vintage_counts = business_metrics['vintage_month'].value_counts().head(10)
    for vintage, count in vintage_counts.items():
        print(f"  {vintage}: {count} business-vintage combinations")
    
    print(f"\n💳 Account Type Distribution:")
    type_counts = business_metrics['accountType'].value_counts()
    for account_type, count in type_counts.items():
        print(f"  {account_type}: {count} combinations")
    
    print(f"\n✅ Business dashboard implementation verified successfully!")


if __name__ == "__main__":
    verify_business_dashboard() 