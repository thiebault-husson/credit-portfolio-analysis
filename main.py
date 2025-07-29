#!/usr/bin/env python3
"""
Highbeam Case Study - Credit Portfolio Analysis
Main entry point for generating comprehensive analysis reports.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.part_1_loan_tape_analysis.loan_tape_analyzer import LoanPortfolioAnalyzer
from src.part_2_orders_data_analysis.orders_data_analyzer import OrdersAnalyzer
from src.reporting.html_report_generator import HTMLReportGenerator


def main():
    """Main function to run the complete analysis."""
    parser = argparse.ArgumentParser(
        description="Highbeam Case Study - Credit Portfolio Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --data-dir ./assets
  python main.py --data-dir ./assets --output-dir ./reports
  python main.py --data-dir ./assets --start-date 2024-01-01 --end-date 2024-12-31
        """
    )
    
    parser.add_argument(
        "--data-dir",
        type=str,
        default="./assets",
        help="Directory containing the data files (default: ./assets)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./reports",
        help="Directory to save the generated reports (default: ./reports)"
    )
    
    parser.add_argument(
        "--start-date",
        type=str,
        help="Start date for analysis (YYYY-MM-DD format)"
    )
    
    parser.add_argument(
        "--end-date", 
        type=str,
        help="End date for analysis (YYYY-MM-DD format)"
    )
    
    parser.add_argument(
        "--report-date",
        type=str,
        default=datetime.now().strftime("%Y-%m-%d"),
        help="Report generation date (default: today)"
    )
    
    args = parser.parse_args()
    
    # Validate data directory
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"Error: Data directory '{data_dir}' does not exist.")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Starting Highbeam Case Study Analysis...")
    print(f"📁 Data directory: {data_dir}")
    print(f"📊 Output directory: {output_dir}")
    
    try:
        # Initialize report generator
        report_generator = HTMLReportGenerator()
        
        # Part 1: Loan Tape Analysis
        print("\n📈 Part 1: Analyzing loan tape data...")
        loan_analyzer = LoanPortfolioAnalyzer(str(data_dir / "part-1" / "test_loan_tape.csv"))
        part1_results = loan_analyzer.analyze_portfolio(
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        # Part 2: Orders Data Analysis  
        print("🛒 Part 2: Analyzing orders and banking data...")
        orders_analyzer = OrdersAnalyzer(
            orders_path=str(data_dir / "part-2" / "test_orders.csv"),
            bank_transactions_path=str(data_dir / "part-2" / "test_bank_transactions.csv")
        )
        part2_results = orders_analyzer.analyze_orders()
        
        # Generate combined report
        print("📋 Generating combined analysis report...")
        
        # Prepare data for combined report
        combined_data = {
            'part1_data': part1_results,
            'part2_data': part2_results,
            'part1_charts': {
                'portfolio_metrics': report_generator._create_portfolio_metrics_chart(part1_results['portfolio_metrics']),
                'yield_metrics': report_generator._create_yield_metrics_chart(part1_results['yield_metrics']),
                'account_type_heatmap': report_generator._create_account_type_heatmap(part1_results['business_metrics'])
            },
            'part2_charts': {
                'ltv_by_cohort': report_generator._create_ltv_by_cohort_chart(part2_results['lifetime_value']),
                'aov_by_cohort': report_generator._create_aov_by_cohort_chart(part2_results['average_order_value'])
            },
            'report_date': args.report_date
        }
        
        # Generate combined report with date-time prefix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"{timestamp}_highbeam_case_study_analysis.html"
        report_path = output_dir / report_filename
        
        report_generator.generate_combined_report(
            combined_data,
            str(report_path)
        )
        
        print(f"✅ Combined report generated: {report_path}")
        print(f"📊 Report contains:")
        print(f"   - Portfolio metrics and yield analysis")
        print(f"   - Customer lifetime value and order patterns")
        print(f"   - Interactive charts and visualizations")
        print(f"   - Executive summary and key insights")
        
        # Open the report in browser
        try:
            import webbrowser
            webbrowser.open(f"file://{report_path.absolute()}")
            print(f"🌐 Opened report in browser")
        except Exception as e:
            print(f"⚠️  Could not open browser: {e}")
            print(f"📄 Please open the report manually: {report_path}")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 