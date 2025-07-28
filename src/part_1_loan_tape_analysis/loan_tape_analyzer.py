"""
Main analyzer class for loan portfolio analysis (Part 1).
"""

import pandas as pd
from typing import Dict, List, Optional
from .loan_tape_data_processor import LoanDataProcessor
from .loan_tape_metrics import PortfolioMetricsCalculator, BusinessMetricsCalculator, YieldMetricsCalculator


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
        self.yield_metrics = None
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
            Dictionary with portfolio metrics, business metrics, yield metrics, and insights
        """
        # Calculate portfolio metrics
        self.portfolio_metrics = PortfolioMetricsCalculator.calculate_portfolio_metrics(
            self.data, start_date, end_date
        )
        
        # Calculate business metrics
        self.business_metrics = BusinessMetricsCalculator.calculate_business_metrics(self.data)
        
        # Calculate yield metrics
        self.yield_metrics = YieldMetricsCalculator(self.data).calculate_all_yield_metrics()
        
        # Generate insights
        self.insights = self._generate_insights()
        
        return {
            'portfolio_metrics': self.portfolio_metrics,
            'business_metrics': self.business_metrics,
            'yield_metrics': self.yield_metrics,
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
    
    def get_yield_metrics(self, filter_active: bool = True) -> Dict:
        """
        Get yield metrics.
        
        Args:
            filter_active: Whether to filter for active accounts only
            
        Returns:
            Dictionary with all yield metrics
        """
        if self.yield_metrics is None:
            self.yield_metrics = YieldMetricsCalculator(self.data).calculate_all_yield_metrics(filter_active)
        return self.yield_metrics
    
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
        
        # Data quality analysis
        insights['data_quality_analysis'] = self._analyze_data_quality()
        
        # Industry insights
        insights['industry_insights'] = self._generate_industry_insights()
        
        return insights
    
    def _analyze_data_quality(self) -> Dict:
        """
        Analyze data quality issues and their industry implications.
        
        Returns:
            Dictionary with data quality analysis
        """
        total_records = len(self.data)
        
        # Negative balances analysis
        negative_balances = self.data[self.data['accountDailyAveragePrincipalBalance'] < 0]
        negative_balance_pct = (len(negative_balances) / total_records) * 100
        
        # Negative revenue analysis
        negative_revenue = self.data[(self.data['lineFeesAccrued'] < 0) | 
                                   (self.data['cardNetInterchangeAccrued'] < 0)]
        negative_revenue_pct = (len(negative_revenue) / total_records) * 100
        
        # Zero balance with revenue analysis
        zero_balance_revenue = self.data[(self.data['accountDailyAveragePrincipalBalance'] == 0) & 
                                       ((self.data['lineFeesAccrued'] > 0) | 
                                        (self.data['cardNetInterchangeAccrued'] > 0))]
        zero_balance_revenue_pct = (len(zero_balance_revenue) / total_records) * 100
        
        return {
            'total_records': total_records,
            'negative_balances': {
                'count': len(negative_balances),
                'percentage': negative_balance_pct,
                'min_balance': negative_balances['accountDailyAveragePrincipalBalance'].min() if len(negative_balances) > 0 else 0,
                'max_balance': negative_balances['accountDailyAveragePrincipalBalance'].max() if len(negative_balances) > 0 else 0,
                'mean_balance': negative_balances['accountDailyAveragePrincipalBalance'].mean() if len(negative_balances) > 0 else 0,
                'status_distribution': negative_balances['accountEndingStatus'].value_counts().to_dict() if len(negative_balances) > 0 else {},
                'type_distribution': negative_balances['accountType'].value_counts().to_dict() if len(negative_balances) > 0 else {}
            },
            'negative_revenue': {
                'count': len(negative_revenue),
                'percentage': negative_revenue_pct,
                'line_fees_negative': len(self.data[self.data['lineFeesAccrued'] < 0]),
                'card_interchange_negative': len(self.data[self.data['cardNetInterchangeAccrued'] < 0]),
                'status_distribution': negative_revenue['accountEndingStatus'].value_counts().to_dict() if len(negative_revenue) > 0 else {}
            },
            'zero_balance_revenue': {
                'count': len(zero_balance_revenue),
                'percentage': zero_balance_revenue_pct,
                'total_revenue': (zero_balance_revenue['lineFeesAccrued'].sum() + 
                                zero_balance_revenue['cardNetInterchangeAccrued'].sum()) if len(zero_balance_revenue) > 0 else 0,
                'average_revenue': (zero_balance_revenue['lineFeesAccrued'].sum() + 
                                  zero_balance_revenue['cardNetInterchangeAccrued'].sum()) / len(zero_balance_revenue) if len(zero_balance_revenue) > 0 else 0,
                'status_distribution': zero_balance_revenue['accountEndingStatus'].value_counts().to_dict() if len(zero_balance_revenue) > 0 else {}
            },
            'data_quality_score': ((total_records - len(negative_balances) - len(negative_revenue) - len(zero_balance_revenue)) / total_records) * 100
        }
    
    def _generate_industry_insights(self) -> Dict:
        """
        Generate industry-specific insights and recommendations.
        
        Returns:
            Dictionary with industry insights
        """
        # Product performance analysis
        line_revenue = self.data['lineFeesAccrued'].sum()
        card_revenue = self.data['cardNetInterchangeAccrued'].sum()
        card_costs = self.data['cardRewardsAccrued'].sum()
        
        # Account type performance
        account_type_performance = {}
        for acc_type in self.data['accountType'].unique():
            type_data = self.data[self.data['accountType'] == acc_type]
            account_type_performance[acc_type] = {
                'count': len(type_data),
                'total_balance': type_data['accountDailyAveragePrincipalBalance'].sum(),
                'total_revenue': type_data['lineFeesAccrued'].sum() + type_data['cardNetInterchangeAccrued'].sum(),
                'total_costs': type_data['cardRewardsAccrued'].sum(),
                'net_revenue': (type_data['lineFeesAccrued'].sum() + type_data['cardNetInterchangeAccrued'].sum()) - type_data['cardRewardsAccrued'].sum(),
                'average_balance': type_data['accountDailyAveragePrincipalBalance'].mean(),
                'delinquency_rate': len(type_data[type_data['accountEndingStatus'] == 'Delinquent']) / len(type_data)
            }
        
        # Portfolio composition insights
        portfolio_composition = {
            'line_products_share': len(self.data[self.data['accountType'] == 'LineRevolving']) / len(self.data),
            'card_products_share': len(self.data[self.data['accountType'].str.startswith('Card')]) / len(self.data),
            'performing_accounts_share': len(self.data[self.data['accountEndingStatus'] == 'Current']) / len(self.data),
            'troubled_accounts_share': len(self.data[self.data['accountEndingStatus'].isin(['Delinquent', 'Default', 'ChargedOff'])]) / len(self.data)
        }
        
        # Revenue concentration analysis
        revenue_concentration = {
            'line_revenue_share': line_revenue / (line_revenue + card_revenue) if (line_revenue + card_revenue) > 0 else 0,
            'card_revenue_share': card_revenue / (line_revenue + card_revenue) if (line_revenue + card_revenue) > 0 else 0,
            'card_cost_ratio': card_costs / card_revenue if card_revenue > 0 else 0,
            'net_revenue_margin': ((line_revenue + card_revenue) - card_costs) / (line_revenue + card_revenue) if (line_revenue + card_revenue) > 0 else 0
        }
        
        # Industry benchmarks and recommendations
        industry_benchmarks = {
            'typical_delinquency_rate': 0.02,  # 2% industry average
            'typical_default_rate': 0.01,      # 1% industry average
            'typical_card_cost_ratio': 0.30,   # 30% typical card rewards cost
            'typical_net_yield': 0.12,         # 12% typical net yield
            'data_quality_threshold': 0.95     # 95% data quality threshold
        }
        
        # Performance vs benchmarks
        current_delinquency = len(self.data[self.data['accountEndingStatus'] == 'Delinquent']) / len(self.data)
        current_default = len(self.data[self.data['accountEndingStatus'] == 'Default']) / len(self.data)
        current_card_cost_ratio = card_costs / card_revenue if card_revenue > 0 else 0
        
        performance_vs_benchmarks = {
            'delinquency_vs_benchmark': 'better' if current_delinquency < industry_benchmarks['typical_delinquency_rate'] else 'worse',
            'default_vs_benchmark': 'better' if current_default < industry_benchmarks['typical_default_rate'] else 'worse',
            'card_cost_vs_benchmark': 'better' if current_card_cost_ratio < industry_benchmarks['typical_card_cost_ratio'] else 'worse',
            'data_quality_vs_benchmark': 'better' if self._analyze_data_quality()['data_quality_score'] > (industry_benchmarks['data_quality_threshold'] * 100) else 'worse'
        }
        
        return {
            'account_type_performance': account_type_performance,
            'portfolio_composition': portfolio_composition,
            'revenue_concentration': revenue_concentration,
            'industry_benchmarks': industry_benchmarks,
            'performance_vs_benchmarks': performance_vs_benchmarks,
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """
        Generate industry recommendations based on analysis.
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Data quality recommendations
        data_quality = self._analyze_data_quality()
        if data_quality['data_quality_score'] < 95:
            recommendations.append("Monitor data quality issues - consider implementing data validation procedures")
        else:
            recommendations.append("Data quality is excellent - current procedures are effective")
        
        # Risk management recommendations
        delinquency_rate = len(self.data[self.data['accountEndingStatus'] == 'Delinquent']) / len(self.data)
        if delinquency_rate > 0.02:
            recommendations.append("Delinquency rate above industry average - review underwriting standards")
        else:
            recommendations.append("Delinquency rate is well-managed - current risk controls are effective")
        
        # Product mix recommendations
        card_share = len(self.data[self.data['accountType'].str.startswith('Card')]) / len(self.data)
        if card_share > 0.3:
            recommendations.append("High card product concentration - consider diversifying product mix")
        else:
            recommendations.append("Product mix is well-diversified - good balance of line and card products")
        
        # Revenue optimization recommendations
        card_costs = self.data['cardRewardsAccrued'].sum()
        card_revenue = self.data['cardNetInterchangeAccrued'].sum()
        if card_costs > card_revenue:
            recommendations.append("Card products operating at loss - review rewards structure and interchange rates")
        else:
            recommendations.append("Card products profitable - current rewards structure is sustainable")
        
        # Portfolio growth recommendations
        total_balance = self.data['accountDailyAveragePrincipalBalance'].sum()
        if total_balance > 0:
            recommendations.append("Portfolio shows healthy growth - continue current expansion strategy")
        else:
            recommendations.append("Monitor portfolio growth - consider growth initiatives")
        
        return recommendations
    
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