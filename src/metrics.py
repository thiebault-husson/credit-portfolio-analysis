"""
Metrics calculations for loan portfolio analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime


class PortfolioMetricsCalculator:
    """Calculate portfolio-level metrics."""
    
    @staticmethod
    def calculate_portfolio_metrics(data: pd.DataFrame, 
                                 start_date: Optional[str] = None,
                                 end_date: Optional[str] = None) -> List[Dict]:
        """
        Calculate portfolio-level metrics by month.
        
        Args:
            data: Preprocessed loan tape data
            start_date: Optional start date filter (YYYY-MM format)
            end_date: Optional end date filter (YYYY-MM format)
            
        Returns:
            List of portfolio metrics by month
        """
        # Filter by date range if provided
        if start_date or end_date:
            data = PortfolioMetricsCalculator._filter_by_date_range(data, start_date, end_date)
        
        # Group by month
        data['month'] = data['snapshotEndingAt'].dt.to_period('M')
        
        # Calculate metrics by month
        monthly_metrics = []
        for month, group in data.groupby('month'):
            metrics = PortfolioMetricsCalculator._calculate_monthly_metrics(group)
            metrics['month'] = month
            monthly_metrics.append(metrics)
        
        return monthly_metrics
    
    @staticmethod
    def _calculate_monthly_metrics(group: pd.DataFrame) -> Dict:
        """
        Calculate metrics for a specific month.
        
        Args:
            group: DataFrame for a specific month
            
        Returns:
            Dictionary with monthly metrics
        """
        # Count accounts by status
        total_accounts = len(group)
        delinquent_accounts = len(group[group['accountEndingStatus'] == 'Delinquent'])
        defaulted_accounts = len(group[group['accountEndingStatus'] == 'Default'])
        charged_off_accounts = len(group[group['accountEndingStatus'] == 'ChargedOff'])
        
        # Calculate rates
        delinquency_rate = delinquent_accounts / total_accounts if total_accounts > 0 else 0
        default_rate = defaulted_accounts / total_accounts if total_accounts > 0 else 0
        charge_off_rate = charged_off_accounts / total_accounts if total_accounts > 0 else 0
        
        # Calculate portfolio size and revenue
        portfolio_size = group['accountDailyAveragePrincipalBalance'].sum()
        total_revenue = (group['lineFeesAccrued'].sum() + 
                        group['cardNetInterchangeAccrued'].sum())
        
        # Calculate yields
        gross_yield = total_revenue / portfolio_size if portfolio_size > 0 else 0
        # Net yield = gross yield - (SOFR + 5%), assuming SOFR is ~5% currently
        net_yield = gross_yield - 0.10  # 5% SOFR + 5% cost of capital
        
        return {
            'total_accounts': total_accounts,
            'delinquency_rate': delinquency_rate,
            'default_rate': default_rate,
            'charge_off_rate': charge_off_rate,
            'portfolio_size': portfolio_size,
            'total_revenue': total_revenue,
            'gross_yield': gross_yield,
            'net_yield': net_yield
        }
    
    @staticmethod
    def _filter_by_date_range(data: pd.DataFrame, 
                             start_date: Optional[str], 
                             end_date: Optional[str]) -> pd.DataFrame:
        """
        Filter data by date range.
        
        Args:
            data: Loan tape data
            start_date: Start date in YYYY-MM format
            end_date: End date in YYYY-MM format
            
        Returns:
            Filtered DataFrame
        """
        if start_date:
            start_dt = pd.to_datetime(f"{start_date}-01")
            data = data[data['snapshotEndingAt'] >= start_dt]
        
        if end_date:
            end_dt = pd.to_datetime(f"{end_date}-01") + pd.DateOffset(months=1) - pd.DateOffset(days=1)
            data = data[data['snapshotEndingAt'] <= end_dt]
        
        return data


class BusinessMetricsCalculator:
    """Calculate business-level metrics."""
    
    @staticmethod
    def calculate_business_metrics(data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate business metrics by monthly vintage.
        
        Args:
            data: Preprocessed loan tape data
            
        Returns:
            DataFrame with business metrics grouped by vintage month
        """
        # Add vintage month (account activation month)
        data['vintage_month'] = data['accountActivatedAt'].dt.to_period('M')
        
        # Calculate account age in months
        data['account_age_months'] = (
            (data['snapshotEndingAt'] - data['accountActivatedAt']).dt.days / 30
        ).round(0)
        
        # Group by business and vintage month
        business_metrics = data.groupby(['businessGuid', 'vintage_month']).agg({
            'accountEndingLimit': 'max',  # Limit
            'accountDailyAveragePrincipalBalance': 'mean',  # Average daily balance
            'account_age_months': 'mean',  # Account age
            'lineFeesAccrued': 'sum',  # Interest revenue
            'cardNetInterchangeAccrued': 'sum',  # Interchange revenue
            'lineEndingApr': 'mean',  # APR
            'accountEndingStatus': lambda x: BusinessMetricsCalculator._get_priority_status(x),  # Status
            'accountPaymentRate': 'mean'  # Payment rate
        }).reset_index()
        
        # Calculate total revenue
        business_metrics['total_revenue'] = (
            business_metrics['lineFeesAccrued'] + 
            business_metrics['cardNetInterchangeAccrued']
        )
        
        # Rename columns for clarity
        business_metrics = business_metrics.rename(columns={
            'accountEndingLimit': 'limit',
            'accountDailyAveragePrincipalBalance': 'average_daily_balance',
            'account_age_months': 'credit_account_age',
            'lineFeesAccrued': 'interest_revenue',
            'cardNetInterchangeAccrued': 'interchange_revenue',
            'lineEndingApr': 'apr',
            'accountEndingStatus': 'borrower_status',
            'accountPaymentRate': 'payment_rate'
        })
        
        return business_metrics
    
    @staticmethod
    def _get_priority_status(statuses: pd.Series) -> str:
        """
        Get the highest priority status from a series of statuses.
        Priority order: Closed > Current > Delinquent > Default > ChargedOff
        
        Args:
            statuses: Series of account statuses
            
        Returns:
            Highest priority status
        """
        priority_order = ['Closed', 'Current', 'Delinquent', 'Default', 'ChargedOff']
        
        for status in priority_order:
            if status in statuses.values:
                return status
        
        return 'Current'  # Default fallback 