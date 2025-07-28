#!/usr/bin/env python3
"""
Unified main entry point for Credit Portfolio Analysis.
Supports Part 1 (Loan Tape Analysis) and Part 2 (Orders Data Analysis).
"""

import argparse
import sys
from typing import Dict, Optional
from src.part_1_loan_tape_analysis.loan_tape_analyzer import LoanPortfolioAnalyzer
from src.part_2_orders_data_analysis.orders_data_analyzer import OrdersAnalyzer


class CreditPortfolioAnalyzer:
    """Unified analyzer for both Part 1 and Part 2 analysis."""
    
    def __init__(self):
        """Initialize the unified analyzer."""
        self.part1_results = None
        self.part2_results = None
        self.part1_analyzer = None
        self.part2_analyzer = None
    
    def run_part1(self) -> Dict:
        """
        Run Part 1: Loan Tape Analysis.
        
        Returns:
            Dictionary with Part 1 results
        """
        print("=" * 60)
        print("PART 1: LOAN TAPE ANALYSIS")
        print("=" * 60)
        
        # Initialize Part 1 analyzer
        self.part1_analyzer = LoanPortfolioAnalyzer("assets/part-1/test_loan_tape.csv")
        
        # Get summary statistics
        summary = self.part1_analyzer.get_summary_stats()
        print(f"\n📊 Data Summary:")
        print(f"   Loaded {summary['total_records']} records")
        print(f"   Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")
        print(f"   Unique businesses: {summary['unique_businesses']}")
        print(f"   Unique accounts: {summary['unique_accounts']}")
        
        # Run analysis
        print(f"\n🔍 Running Part 1 analysis...")
        self.part1_results = self.part1_analyzer.analyze_portfolio()
        
        # Display results
        self._display_part1_results()
        
        return self.part1_results
    
    def run_part2(self) -> Dict:
        """
        Run Part 2: Orders Data Analysis.
        
        Returns:
            Dictionary with Part 2 results
        """
        print("=" * 60)
        print("PART 2: ORDERS DATA ANALYSIS")
        print("=" * 60)
        
        # Initialize Part 2 analyzer
        self.part2_analyzer = OrdersAnalyzer(
            "assets/part-2/test_orders.csv",
            "assets/part-2/test_bank_transactions.csv"
        )
        
        # Get summary statistics
        summary = self.part2_analyzer.get_summary_stats()
        print(f"\n📊 Data Summary:")
        print(f"   Loaded {summary['total_orders']} orders")
        print(f"   Total customers: {summary['total_customers']}")
        print(f"   Date range: {summary['date_range']['start']} to {summary['date_range']['end']}")
        print(f"   Gross revenue: ${summary['gross_revenue']:,.2f}")
        print(f"   Net revenue: ${summary['net_revenue']:,.2f}")
        print(f"   Total refunds: ${summary['total_refunds']:,.2f}")
        print(f"   Total discounts: ${summary['total_discounts']:,.2f}")
        print(f"   Average order value: ${summary['average_order_value']:,.2f}")
        print(f"   Bank transactions: {summary['bank_transactions_count']}")
        
        # Run analysis
        print(f"\n🔍 Running Part 2 analysis...")
        self.part2_results = self.part2_analyzer.analyze_orders()
        
        # Display results
        self._display_part2_results()
        
        return self.part2_results
    
    def run_complete(self) -> Dict:
        """
        Run both Part 1 and Part 2 analysis.
        
        Returns:
            Dictionary with combined results
        """
        print("=" * 60)
        print("COMPLETE CREDIT PORTFOLIO ANALYSIS")
        print("=" * 60)
        
        # Run both parts
        part1_results = self.run_part1()
        part2_results = self.run_part2()
        
        # Generate combined insights
        combined_insights = self._generate_combined_insights(part1_results, part2_results)
        
        # Display combined insights
        self._display_combined_insights(combined_insights)
        
        return {
            'part1': part1_results,
            'part2': part2_results,
            'combined_insights': combined_insights
        }
    
    def _display_part1_results(self):
        """Display Part 1 results."""
        if not self.part1_results:
            return
        
        # Portfolio metrics
        portfolio_metrics = self.part1_results['portfolio_metrics']
        if portfolio_metrics:
            latest_month = portfolio_metrics[-1]
            print(f"\n📈 Portfolio Metrics (Latest Month):")
            print(f"   Total Accounts: {latest_month['total_accounts']}")
            print(f"   Portfolio Size: ${latest_month['portfolio_size']:,.2f}")
            print(f"   Delinquency Rate: {latest_month['delinquency_rate']:.2%}")
            print(f"   Default Rate: {latest_month['default_rate']:.2%}")
            print(f"   Charge-off Rate: {latest_month['charge_off_rate']:.2%}")
            print(f"   Gross Yield: {latest_month['gross_yield']:.2%}")
            print(f"   Net Yield: {latest_month['net_yield']:.2%}")
        
        # Business metrics
        business_metrics = self.part1_results['business_metrics']
        if not business_metrics.empty:
            print(f"\n🏢 Business Metrics:")
            print(f"   Total business-vintage combinations: {len(business_metrics)}")
        
        # Insights
        insights = self.part1_results['insights']
        if insights:
            print(f"\n💡 Key Insights:")
            print(f"   Total Portfolio Size: ${insights['portfolio_growth']['total_portfolio_size']:,.2f}")
            print(f"   Total Businesses: {insights['portfolio_growth']['total_businesses']}")
            print(f"   Delinquency Rate: {insights['risk_analysis']['delinquency_rate']:.2%}")
    
    def _display_part2_results(self):
        """Display Part 2 results."""
        if not self.part2_results:
            return
        
        # LTV
        ltv_analysis = self.part2_results['lifetime_value']
        print(f"\n💰 Lifetime Value (LTV):")
        print(f"   Average LTV: ${ltv_analysis['summary']['average_ltv']:,.2f}")
        print(f"   Total customers: {ltv_analysis['summary']['total_customers']}")
        
        # AOV
        aov_analysis = self.part2_results['average_order_value']
        print(f"\n📦 Average Order Value (AOV):")
        print(f"   Average AOV: ${aov_analysis['summary']['average_aov']:,.2f}")
        print(f"   Total orders: {aov_analysis['summary']['total_orders']}")
        
        # CAC
        cac_analysis = self.part2_results['customer_acquisition_cost']
        print(f"\n🎯 Customer Acquisition Cost (CAC):")
        print(f"   Estimated CAC: ${cac_analysis['summary']['estimated_cac']:,.2f}")
        print(f"   LTV/CAC ratio: {cac_analysis['summary']['ltv_cac_ratio']:.2f}")
        
        # Insights
        insights = self.part2_results['insights']
        if insights:
            print(f"\n💡 Key Insights:")
            behavior = insights['customer_behavior']
            print(f"   Repeat customer rate: {behavior['repeat_customer_rate']:.2%}")
            print(f"   Average orders per customer: {behavior['average_orders_per_customer']:.2f}")
    
    def _generate_combined_insights(self, part1_results: Dict, part2_results: Dict) -> Dict:
        """Generate combined insights from both parts."""
        combined = {
            'portfolio_summary': {
                'loan_portfolio_size': part1_results['insights']['portfolio_growth']['total_portfolio_size'],
                'orders_revenue': part2_results['average_order_value']['summary']['total_revenue'],
                'total_businesses': part1_results['insights']['portfolio_growth']['total_businesses'],
                'total_customers': part2_results['lifetime_value']['summary']['total_customers']
            },
            'risk_analysis': {
                'loan_delinquency_rate': part1_results['insights']['risk_analysis']['delinquency_rate'],
                'customer_repeat_rate': part2_results['insights']['customer_behavior']['repeat_customer_rate']
            },
            'profitability': {
                'loan_net_yield': part1_results['portfolio_metrics'][-1]['net_yield'] if part1_results['portfolio_metrics'] else 0,
                'orders_ltv_cac_ratio': part2_results['customer_acquisition_cost']['summary']['ltv_cac_ratio']
            }
        }
        return combined
    
    def _display_combined_insights(self, combined_insights: Dict):
        """Display combined insights."""
        print("\n" + "=" * 60)
        print("COMBINED INSIGHTS")
        print("=" * 60)
        
        portfolio = combined_insights['portfolio_summary']
        print(f"\n📊 Portfolio Summary:")
        print(f"   Loan Portfolio: ${portfolio['loan_portfolio_size']:,.2f}")
        print(f"   Orders Revenue: ${portfolio['orders_revenue']:,.2f}")
        print(f"   Total Businesses: {portfolio['total_businesses']}")
        print(f"   Total Customers: {portfolio['total_customers']}")
        
        risk = combined_insights['risk_analysis']
        print(f"\n⚠️ Risk Analysis:")
        print(f"   Loan Delinquency Rate: {risk['loan_delinquency_rate']:.2%}")
        print(f"   Customer Repeat Rate: {risk['customer_repeat_rate']:.2%}")
        
        profitability = combined_insights['profitability']
        print(f"\n💰 Profitability:")
        print(f"   Loan Net Yield: {profitability['loan_net_yield']:.2%}")
        print(f"   Orders LTV/CAC Ratio: {profitability['orders_ltv_cac_ratio']:.2f}")
    
    def generate_html_report(self, data: Dict, report_type: str = "complete") -> str:
        """
        Generate HTML report (placeholder for future implementation).
        
        Args:
            data: Analysis results
            report_type: Type of report (part1, part2, complete)
            
        Returns:
            HTML string
        """
        # TODO: Implement HTML report generation
        return f"<html><body><h1>{report_type.upper()} Report</h1><p>HTML report generation coming soon...</p></body></html>"


def main():
    """Main entry point with command line argument parsing."""
    parser = argparse.ArgumentParser(description="Credit Portfolio Analysis")
    parser.add_argument(
        "--part", 
        choices=["1", "2", "all"], 
        default="all",
        help="Which part to run (1=Loan Tape, 2=Orders Data, all=Both)"
    )
    parser.add_argument(
        "--output", 
        choices=["console", "html"], 
        default="console",
        help="Output format (console or html)"
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = CreditPortfolioAnalyzer()
    
    # Run analysis based on arguments
    if args.part == "1":
        results = analyzer.run_part1()
    elif args.part == "2":
        results = analyzer.run_part2()
    else:  # "all"
        results = analyzer.run_complete()
    
    # Generate output
    if args.output == "html":
        html_report = analyzer.generate_html_report(results, args.part)
        print("\n" + "=" * 60)
        print("HTML REPORT GENERATED")
        print("=" * 60)
        print(html_report)
    else:
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 