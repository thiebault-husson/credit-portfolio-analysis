#!/usr/bin/env python3
"""
Main entry point for Credit Portfolio Analysis
"""

import json
import pandas as pd
from src.analyzer import LoanPortfolioAnalyzer


def main():
    """Run the complete portfolio analysis."""
    
    print("=" * 60)
    print("CREDIT PORTFOLIO ANALYSIS")
    print("=" * 60)
    
    # Initialize analyzer
    print("\n1. Loading loan tape data...")
    analyzer = LoanPortfolioAnalyzer("assets/part-1/test_loan_tape.csv")
    
    # Get summary statistics
    summary = analyzer.get_summary_stats()
    print(f"   Loaded {summary['total_records']} records")
    print(f"   Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")
    print(f"   Unique businesses: {summary['unique_businesses']}")
    print(f"   Unique accounts: {summary['unique_accounts']}")
    
    # Run complete analysis
    print("\n2. Running portfolio analysis...")
    results = analyzer.analyze_portfolio()
    
    # Display portfolio metrics
    print("\n" + "=" * 40)
    print("PORTFOLIO METRICS BY MONTH")
    print("=" * 40)
    
    portfolio_metrics = results['portfolio_metrics']
    if portfolio_metrics:
        # Display the most recent month's metrics
        latest_month = portfolio_metrics[-1]
        print(f"Latest Month ({latest_month['month']}):")
        print(f"  Total Accounts: {latest_month['total_accounts']}")
        print(f"  Portfolio Size: ${latest_month['portfolio_size']:,.2f}")
        print(f"  Delinquency Rate: {latest_month['delinquency_rate']:.2%}")
        print(f"  Default Rate: {latest_month['default_rate']:.2%}")
        print(f"  Charge-off Rate: {latest_month['charge_off_rate']:.2%}")
        print(f"  Gross Yield: {latest_month['gross_yield']:.2%}")
        print(f"  Net Yield: {latest_month['net_yield']:.2%}")
        print(f"  Total Revenue: ${latest_month['total_revenue']:,.2f}")
    
    # Display business metrics
    print("\n" + "=" * 40)
    print("BUSINESS METRICS BY VINTAGE")
    print("=" * 40)
    
    business_metrics = results['business_metrics']
    if not business_metrics.empty:
        print(f"Total business-vintage combinations: {len(business_metrics)}")
        print("\nSample business metrics:")
        print(business_metrics.head().to_string(index=False))
    
    # Display insights
    print("\n" + "=" * 40)
    print("KEY INSIGHTS")
    print("=" * 40)
    
    insights = results['insights']
    
    # Portfolio growth insights
    growth = insights['portfolio_growth']
    print(f"Portfolio Growth:")
    print(f"  Total Portfolio Size: ${growth['total_portfolio_size']:,.2f}")
    print(f"  Total Businesses: {growth['total_businesses']}")
    print(f"  Total Accounts: {growth['total_accounts']}")
    print(f"  Average Account Size: ${growth['average_account_size']:,.2f}")
    print(f"  Growth Trend: {growth['portfolio_growth_trend']}")
    
    # Account type distribution
    print(f"\nAccount Type Distribution:")
    for account_type, count in insights['account_type_distribution'].items():
        print(f"  {account_type}: {count}")
    
    # Status distribution
    print(f"\nAccount Status Distribution:")
    for status, count in insights['status_distribution'].items():
        print(f"  {status}: {count}")
    
    # Revenue analysis
    revenue = insights['revenue_analysis']
    print(f"\nRevenue Analysis:")
    print(f"  Total Revenue: ${revenue['total_revenue']:,.2f}")
    print(f"  Interest Revenue: ${revenue['interest_revenue']:,.2f}")
    print(f"  Interchange Revenue: ${revenue['interchange_revenue']:,.2f}")
    print(f"  Revenue per Account: ${revenue['revenue_per_account']:,.2f}")
    
    # Risk analysis
    risk = insights['risk_analysis']
    print(f"\nRisk Analysis:")
    print(f"  Delinquency Rate: {risk['delinquency_rate']:.2%}")
    print(f"  Default Rate: {risk['default_rate']:.2%}")
    print(f"  Charge-off Rate: {risk['charge_off_rate']:.2%}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main() 