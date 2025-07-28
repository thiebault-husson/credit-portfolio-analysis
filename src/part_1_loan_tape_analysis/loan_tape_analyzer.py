"""
Main analyzer class for loan portfolio analysis (Part 1).
"""

import pandas as pd
from typing import Dict, List, Optional
from .loan_tape_data_processor import LoanDataProcessor
from .loan_tape_metrics import PortfolioMetricsCalculator, BusinessMetricsCalculator


class LoanPortfolioAnalyzer:
    """Main class for loan portfolio analysis (Part 1)."""
    
    def __init__(self, data_path: str):
        """
        Initialize the analyzer with loan tape data.
        
        Args:
            data_path: Path to the loan tape CSV file
        """
        self.data = LoanDataProcessor.load_loan_tape(data_path)
        self.portfolio_metrics = None
        self.business_metrics = None
        self.insights = None
    
    def analyze_portfolio(self, 
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> Dict:
        """
        Run complete portfolio analysis.
        
        Args:
            start_date: Optional start date filter (YYYY-MM format)
            end_date: Optional end date filter (YYYY-MM format)
            
        Returns:
            Dictionary with portfolio metrics, business metrics, and insights
        """
        # Calculate portfolio metrics
        self.portfolio_metrics = PortfolioMetricsCalculator.calculate_portfolio_metrics(
            self.data, start_date, end_date
        )
        
        # Calculate business metrics
        self.business_metrics = BusinessMetricsCalculator.calculate_business_metrics(self.data)
        
        # Generate insights
        self.insights = self._generate_insights()
        
        return {
            'portfolio_metrics': self.portfolio_metrics,
            'business_metrics': self.business_metrics,
            'insights': self.insights
        }
    
    def get_portfolio_metrics(self, 
                            start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> List[Dict]:
        """
        Get portfolio-level metrics.
        
        Args:
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of portfolio metrics by month
        """
        return PortfolioMetricsCalculator.calculate_portfolio_metrics(
            self.data, start_date, end_date
        )
    
    def get_business_metrics(self) -> pd.DataFrame:
        """
        Get business metrics by vintage.
        
        Returns:
            DataFrame with business metrics grouped by vintage month
        """
        return BusinessMetricsCalculator.calculate_business_metrics(self.data)
    
    def get_insights(self) -> Dict:
        """
        Get insights from the data.
        
        Returns:
            Dictionary with key insights and patterns
        """
        if self.insights is None:
            self.insights = self._generate_insights()
        return self.insights
    
    def _generate_insights(self) -> Dict:
        """
        Generate interesting insights from the loan tape data.
        
        Returns:
            Dictionary with insights and patterns
        """
        insights = {}
        
        # Portfolio size trends
        monthly_data = self.data.groupby(self.data['snapshotEndingAt'].dt.to_period('M')).agg({
            'accountDailyAveragePrincipalBalance': 'sum',
            'businessGuid': 'nunique',
            'capitalAccountGuid': 'nunique'
        }).reset_index()
        
        insights['portfolio_growth'] = {
            'total_portfolio_size': self.data['accountDailyAveragePrincipalBalance'].sum(),
            'total_businesses': self.data['businessGuid'].nunique(),
            'total_accounts': self.data['capitalAccountGuid'].nunique(),
            'average_account_size': self.data['accountDailyAveragePrincipalBalance'].mean(),
            'portfolio_growth_trend': 'increasing' if len(monthly_data) > 1 and 
                monthly_data['accountDailyAveragePrincipalBalance'].iloc[-1] > 
                monthly_data['accountDailyAveragePrincipalBalance'].iloc[0] else 'stable'
        }
        
        # Account type distribution
        account_type_dist = self.data['accountType'].value_counts()
        insights['account_type_distribution'] = account_type_dist.to_dict()
        
        # Status distribution
        status_dist = self.data['accountEndingStatus'].value_counts()
        insights['status_distribution'] = status_dist.to_dict()
        
        # Revenue analysis
        total_revenue = (self.data['lineFeesAccrued'].sum() + 
                        self.data['cardNetInterchangeAccrued'].sum())
        insights['revenue_analysis'] = {
            'total_revenue': total_revenue,
            'interest_revenue': self.data['lineFeesAccrued'].sum(),
            'interchange_revenue': self.data['cardNetInterchangeAccrued'].sum(),
            'revenue_per_account': total_revenue / len(self.data) if len(self.data) > 0 else 0
        }
        
        # Risk analysis
        risk_metrics = {
            'delinquency_rate': len(self.data[self.data['accountEndingStatus'] == 'Delinquent']) / len(self.data),
            'default_rate': len(self.data[self.data['accountEndingStatus'] == 'Default']) / len(self.data),
            'charge_off_rate': len(self.data[self.data['accountEndingStatus'] == 'ChargedOff']) / len(self.data)
        }
        insights['risk_analysis'] = risk_metrics
        
        # Business analysis
        if 'businessGuid' in self.data.columns:
            business_count = self.data['businessGuid'].nunique()
            insights['business_analysis'] = {
                'total_businesses': business_count,
                'accounts_per_business': len(self.data) / business_count if business_count > 0 else 0
            }
        
        return insights
    
    def get_summary_stats(self) -> Dict:
        """
        Get summary statistics for the portfolio.
        
        Returns:
            Dictionary with summary statistics
        """
        return {
            'total_records': len(self.data),
            'date_range': {
                'start': self.data['snapshotEndingAt'].min(),
                'end': self.data['snapshotEndingAt'].max()
            },
            'unique_businesses': self.data['businessGuid'].nunique(),
            'unique_accounts': self.data['capitalAccountGuid'].nunique(),
            'account_types': self.data['accountType'].nunique(),
            'statuses': self.data['accountEndingStatus'].nunique()
        } 