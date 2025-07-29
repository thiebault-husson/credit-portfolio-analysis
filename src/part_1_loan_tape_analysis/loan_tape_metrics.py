"""
Metrics calculations for loan portfolio analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from functools import lru_cache
import re


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
        Calculate metrics for a specific month using industry-standard approach.
        
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
        closed_accounts = len(group[group['accountEndingStatus'] == 'Closed'])
        current_accounts = len(group[group['accountEndingStatus'] == 'Current'])
        
        # Calculate rates
        delinquency_rate = delinquent_accounts / total_accounts if total_accounts > 0 else 0
        default_rate = defaulted_accounts / total_accounts if total_accounts > 0 else 0
        charge_off_rate = charged_off_accounts / total_accounts if total_accounts > 0 else 0
        
        # Calculate portfolio size using industry-standard approach
        # Denominator: balances including Current, Delinquent, Default
        denom_mask = group['accountEndingStatus'].isin(['Current', 'Delinquent', 'Default'])
        portfolio_size = group.loc[denom_mask, 'accountDailyAveragePrincipalBalance'].sum()
        
        # Calculate revenue using industry-standard approach
        # Numerator: revenue only from Current and Delinquent
        num_mask = group['accountEndingStatus'].isin(['Current', 'Delinquent'])
        total_revenue = (group.loc[num_mask, 'lineFeesAccrued'].sum() + 
                        group.loc[num_mask, 'cardNetInterchangeAccrued'].sum())
        
        # Calculate yields using industry-standard approach
        gross_yield = (total_revenue / portfolio_size) * 12 if portfolio_size > 0 else 0  # Monthly annualization
        # Net yield = gross yield - (SOFR + 5%), assuming SOFR is ~5% currently
        net_yield = gross_yield - 0.10  # 10% cost of capital
        
        return {
            'total_accounts': total_accounts,
            'current_accounts': current_accounts,
            'delinquent_accounts': delinquent_accounts,
            'defaulted_accounts': defaulted_accounts,
            'charged_off_accounts': charged_off_accounts,
            'closed_accounts': closed_accounts,
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

    @staticmethod
    def calculate_portfolio_wide_rates(data: pd.DataFrame) -> Dict:
        """
        Calculate portfolio-wide rates across all data (not just latest month).
        
        Args:
            data: Preprocessed loan tape data
            
        Returns:
            Dictionary with portfolio-wide rates
        """
        # Count total accounts and status counts across all data
        total_accounts = len(data)
        delinquent_accounts = len(data[data['accountEndingStatus'] == 'Delinquent'])
        defaulted_accounts = len(data[data['accountEndingStatus'] == 'Default'])
        charged_off_accounts = len(data[data['accountEndingStatus'] == 'ChargedOff'])
        closed_accounts = len(data[data['accountEndingStatus'] == 'Closed'])
        current_accounts = len(data[data['accountEndingStatus'] == 'Current'])
        
        # Calculate portfolio-wide rates
        delinquency_rate = delinquent_accounts / total_accounts if total_accounts > 0 else 0
        default_rate = defaulted_accounts / total_accounts if total_accounts > 0 else 0
        charge_off_rate = charged_off_accounts / total_accounts if total_accounts > 0 else 0
        
        return {
            'total_accounts': total_accounts,
            'current_accounts': current_accounts,
            'delinquent_accounts': delinquent_accounts,
            'defaulted_accounts': defaulted_accounts,
            'charged_off_accounts': charged_off_accounts,
            'closed_accounts': closed_accounts,
            'delinquency_rate': delinquency_rate,
            'default_rate': default_rate,
            'charge_off_rate': charge_off_rate
        }


class YieldMetricsCalculator:
    """
    Calculate comprehensive yield metrics using industry-standard approach.
    
    Implements yield metrics with proper status-based filtering:
    - Current: Include both balances and revenue fully
    - Delinquent: Include balances fully, include revenue if accrued
    - Default: Include balances in denominator, exclude revenue from numerator
    - ChargedOff: Exclude from both numerator and denominator
    - Closed: Exclude from both numerator and denominator
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize calculator with preprocessed data.
        
        Args:
            data: Clean DataFrame with loan tape data
        """
        self.raw_data = data.copy()
        self.data = self._preprocess_data()
        
    def _parse_currency(self, value) -> float:
        """Parse currency string to float."""
        if pd.isna(value) or value == '':
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = re.sub(r'[$,]', '', value.strip())
            try:
                return float(cleaned)
            except ValueError:
                return 0.0
        return 0.0
    
    def _preprocess_data(self) -> pd.DataFrame:
        """Preprocess data once for all calculations."""
        df = self.raw_data.copy()
        
        # Parse currency columns
        currency_columns = [
            'lineFeesAccrued', 'cardNetInterchangeAccrued', 'cardRewardsAccrued',
            'lineDailyAveragePrincipalBalance', 'cardDailyAveragePrincipalBalance',
            'accountDailyAveragePrincipalBalance'
        ]
        
        for col in currency_columns:
            if col in df.columns:
                df[col] = df[col].apply(self._parse_currency)
        
        # Parse date columns
        date_columns = ['snapshotBeginningAt', 'snapshotEndingAt', 'accountActivatedAt']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        
        return df
    
    def _get_filtered_data(self, filter_active: bool = True) -> pd.DataFrame:
        """Get filtered data based on criteria."""
        df = self.data.copy()
        
        if filter_active:
            # Filter out charged off accounts for cleaner analysis
            df = df[df['accountEndingStatus'] != 'ChargedOff']
        
        return df
    
    def calculate_gross_portfolio_yield(self, filter_active: bool = True) -> Dict:
        """
        Calculate Gross Portfolio Yield using industry-standard approach.
        
        Formula: (Revenue from Current+Delinquent / Balance from Current+Delinquent+Default) × (365/period_days)
        
        Args:
            filter_active: Whether to filter for active accounts only
            
        Returns:
            Dictionary with GPY metrics
        """
        df = self._get_filtered_data(filter_active)
        
        # Calculate period days for proper annualization
        df['period_days'] = (df['snapshotEndingAt'] - df['snapshotBeginningAt']).dt.days
        df['period_days'] = df['period_days'].clip(lower=1)  # Ensure no division by zero
        
        # Denominator: balances including Current, Delinquent, Default
        denom_mask = df['accountEndingStatus'].isin(['Current', 'Delinquent', 'Default'])
        total_balance = df.loc[denom_mask, 'accountDailyAveragePrincipalBalance'].sum()
        
        # Numerator: revenue only from Current and Delinquent
        num_mask = df['accountEndingStatus'].isin(['Current', 'Delinquent'])
        total_revenue = (df.loc[num_mask, 'lineFeesAccrued'].sum() + 
                        df.loc[num_mask, 'cardNetInterchangeAccrued'].sum())
        
        # Calculate average period days for annualization
        avg_period_days = df.loc[num_mask, 'period_days'].mean()
        if pd.isna(avg_period_days) or avg_period_days == 0:
            avg_period_days = 30  # Default to 30 days if calculation fails
        
        # Calculate GPY with proper annualization
        gross_portfolio_yield = (total_revenue / total_balance) * (365 / avg_period_days) if total_balance > 0 else 0
        
        # Calculate component breakdowns
        current_revenue = df.loc[df['accountEndingStatus'] == 'Current', ['lineFeesAccrued', 'cardNetInterchangeAccrued']].sum().sum()
        delinquent_revenue = df.loc[df['accountEndingStatus'] == 'Delinquent', ['lineFeesAccrued', 'cardNetInterchangeAccrued']].sum().sum()
        
        current_balance = df.loc[df['accountEndingStatus'] == 'Current', 'accountDailyAveragePrincipalBalance'].sum()
        delinquent_balance = df.loc[df['accountEndingStatus'] == 'Delinquent', 'accountDailyAveragePrincipalBalance'].sum()
        default_balance = df.loc[df['accountEndingStatus'] == 'Default', 'accountDailyAveragePrincipalBalance'].sum()
        
        return {
            'gross_portfolio_yield': gross_portfolio_yield,
            'total_revenue': total_revenue,
            'total_balance': total_balance,
            'current_revenue': current_revenue,
            'delinquent_revenue': delinquent_revenue,
            'current_balance': current_balance,
            'delinquent_balance': delinquent_balance,
            'default_balance': default_balance,
            'accounts_included_revenue': len(df[num_mask]),
            'accounts_included_balance': len(df[denom_mask]),
            'avg_period_days': avg_period_days,
            'annualization_factor': 365 / avg_period_days
        }
    
    def calculate_net_portfolio_yield(self, filter_active: bool = True) -> Dict:
        """
        Calculate Net Portfolio Yield using industry-standard approach.
        
        Formula: ((Revenue from Current+Delinquent - Costs) / Balance from Current+Delinquent+Default) × (365/period_days)
        
        Args:
            filter_active: Whether to filter for active accounts only
            
        Returns:
            Dictionary with NPY metrics
        """
        df = self._get_filtered_data(filter_active)
        
        # Calculate period days for proper annualization
        df['period_days'] = (df['snapshotEndingAt'] - df['snapshotBeginningAt']).dt.days
        df['period_days'] = df['period_days'].clip(lower=1)  # Ensure no division by zero
        
        # Denominator: balances including Current, Delinquent, Default
        denom_mask = df['accountEndingStatus'].isin(['Current', 'Delinquent', 'Default'])
        total_balance = df.loc[denom_mask, 'accountDailyAveragePrincipalBalance'].sum()
        
        # Numerator: revenue only from Current and Delinquent, minus costs
        num_mask = df['accountEndingStatus'].isin(['Current', 'Delinquent'])
        total_revenue = (df.loc[num_mask, 'lineFeesAccrued'].sum() + 
                        df.loc[num_mask, 'cardNetInterchangeAccrued'].sum())
        
        # Costs: card rewards from Current and Delinquent accounts
        total_costs = df.loc[num_mask, 'cardRewardsAccrued'].sum()
        
        # Calculate average period days for annualization
        avg_period_days = df.loc[num_mask, 'period_days'].mean()
        if pd.isna(avg_period_days) or avg_period_days == 0:
            avg_period_days = 30  # Default to 30 days if calculation fails
        
        # Calculate NPY with proper annualization
        net_revenue = total_revenue - total_costs
        net_portfolio_yield = (net_revenue / total_balance) * (365 / avg_period_days) if total_balance > 0 else 0
        
        return {
            'net_portfolio_yield': net_portfolio_yield,
            'total_revenue': total_revenue,
            'total_costs': total_costs,
            'net_revenue': net_revenue,
            'total_balance': total_balance,
            'cost_ratio': (total_costs / total_revenue * 100) if total_revenue > 0 else 0,
            'avg_period_days': avg_period_days,
            'annualization_factor': 365 / avg_period_days
        }
    
    def calculate_net_portfolio_yield_after_cost_of_capital(self, filter_active: bool = True) -> Dict:
        """
        Calculate Net Portfolio Yield After Cost of Capital using industry-standard approach.
        
        Formula: Net Portfolio Yield - (SOFR + 5%) = NPY - 10%
        
        Args:
            filter_active: Whether to filter for active accounts only
            
        Returns:
            Dictionary with NPY After Cost of Capital metrics
        """
        # First calculate the base Net Portfolio Yield
        npy_result = self.calculate_net_portfolio_yield(filter_active)
        
        # Cost of capital: SOFR + 5% = 10% (assuming SOFR is ~5% currently)
        cost_of_capital = 0.10
        
        # Calculate NPY after cost of capital
        npy_after_coc = npy_result['net_portfolio_yield'] - cost_of_capital
        
        return {
            'net_portfolio_yield_after_coc': npy_after_coc,
            'base_net_portfolio_yield': npy_result['net_portfolio_yield'],
            'cost_of_capital': cost_of_capital,
            'total_revenue': npy_result['total_revenue'],
            'total_costs': npy_result['total_costs'],
            'net_revenue': npy_result['net_revenue'],
            'total_balance': npy_result['total_balance'],
            'cost_ratio': npy_result['cost_ratio'],
            'avg_period_days': npy_result['avg_period_days'],
            'annualization_factor': npy_result['annualization_factor']
        }
    
    def calculate_line_gross_portfolio_yield(self, filter_active: bool = True) -> Dict:
        """
        Calculate Line Gross Portfolio Yield using industry-standard approach.
        
        Formula: (Line Revenue from Current+Delinquent / Line Balance from Current+Delinquent+Default) × (365/period_days)
        """
        df = self._get_filtered_data(filter_active)
        
        # Calculate period days for proper annualization
        df['period_days'] = (df['snapshotEndingAt'] - df['snapshotBeginningAt']).dt.days
        df['period_days'] = df['period_days'].clip(lower=1)  # Ensure no division by zero
        
        # Denominator: line balances including Current, Delinquent, Default
        denom_mask = df['accountEndingStatus'].isin(['Current', 'Delinquent', 'Default'])
        total_line_balance = df.loc[denom_mask, 'lineDailyAveragePrincipalBalance'].sum()
        
        # Numerator: line revenue only from Current and Delinquent
        num_mask = df['accountEndingStatus'].isin(['Current', 'Delinquent'])
        total_line_revenue = df.loc[num_mask, 'lineFeesAccrued'].sum()
        
        # Calculate average period days for annualization
        avg_period_days = df.loc[num_mask, 'period_days'].mean()
        if pd.isna(avg_period_days) or avg_period_days == 0:
            avg_period_days = 30  # Default to 30 days if calculation fails
        
        # Calculate line GPY with proper annualization
        line_gross_portfolio_yield = (total_line_revenue / total_line_balance) * (365 / avg_period_days) if total_line_balance > 0 else 0
        
        return {
            'line_gross_portfolio_yield': line_gross_portfolio_yield,
            'total_line_revenue': total_line_revenue,
            'total_line_balance': total_line_balance,
            'accounts_with_line_revenue': len(df[num_mask & (df['lineFeesAccrued'] > 0)]),
            'accounts_with_line_balance': len(df[denom_mask & (df['lineDailyAveragePrincipalBalance'] > 0)]),
            'avg_period_days': avg_period_days,
            'annualization_factor': 365 / avg_period_days
        }
    
    def calculate_card_gross_portfolio_yield(self, filter_active: bool = True) -> Dict:
        """
        Calculate Card Gross Portfolio Yield using industry-standard approach.
        
        Formula: (Card Revenue from Current+Delinquent / Card Balance from Current+Delinquent+Default) × (365/period_days)
        """
        df = self._get_filtered_data(filter_active)
        
        # Calculate period days for proper annualization
        df['period_days'] = (df['snapshotEndingAt'] - df['snapshotBeginningAt']).dt.days
        df['period_days'] = df['period_days'].clip(lower=1)  # Ensure no division by zero
        
        # Denominator: card balances including Current, Delinquent, Default
        denom_mask = df['accountEndingStatus'].isin(['Current', 'Delinquent', 'Default'])
        total_card_balance = df.loc[denom_mask, 'cardDailyAveragePrincipalBalance'].sum()
        
        # Numerator: card revenue only from Current and Delinquent
        num_mask = df['accountEndingStatus'].isin(['Current', 'Delinquent'])
        total_card_revenue = df.loc[num_mask, 'cardNetInterchangeAccrued'].sum()
        
        # Calculate average period days for annualization
        avg_period_days = df.loc[num_mask, 'period_days'].mean()
        if pd.isna(avg_period_days) or avg_period_days == 0:
            avg_period_days = 30  # Default to 30 days if calculation fails
        
        # Calculate card GPY with proper annualization
        card_gross_portfolio_yield = (total_card_revenue / total_card_balance) * (365 / avg_period_days) if total_card_balance > 0 else 0
        
        return {
            'card_gross_portfolio_yield': card_gross_portfolio_yield,
            'total_card_revenue': total_card_revenue,
            'total_card_balance': total_card_balance,
            'accounts_with_card_revenue': len(df[num_mask & (df['cardNetInterchangeAccrued'] > 0)]),
            'accounts_with_card_balance': len(df[denom_mask & (df['cardDailyAveragePrincipalBalance'] > 0)]),
            'avg_period_days': avg_period_days,
            'annualization_factor': 365 / avg_period_days
        }
    
    def calculate_card_net_portfolio_yield(self, filter_active: bool = True) -> Dict:
        """
        Calculate Card Net Portfolio Yield using industry-standard approach.
        
        Formula: ((Card Revenue from Current+Delinquent - Card Costs) / Card Balance from Current+Delinquent+Default) × (365/period_days)
        """
        df = self._get_filtered_data(filter_active)
        
        # Calculate period days for proper annualization
        df['period_days'] = (df['snapshotEndingAt'] - df['snapshotBeginningAt']).dt.days
        df['period_days'] = df['period_days'].clip(lower=1)  # Ensure no division by zero
        
        # Denominator: card balances including Current, Delinquent, Default
        denom_mask = df['accountEndingStatus'].isin(['Current', 'Delinquent', 'Default'])
        total_card_balance = df.loc[denom_mask, 'cardDailyAveragePrincipalBalance'].sum()
        
        # Numerator: card revenue and costs only from Current and Delinquent
        num_mask = df['accountEndingStatus'].isin(['Current', 'Delinquent'])
        total_card_revenue = df.loc[num_mask, 'cardNetInterchangeAccrued'].sum()
        total_card_costs = df.loc[num_mask, 'cardRewardsAccrued'].sum()
        
        # Calculate average period days for annualization
        avg_period_days = df.loc[num_mask, 'period_days'].mean()
        if pd.isna(avg_period_days) or avg_period_days == 0:
            avg_period_days = 30  # Default to 30 days if calculation fails
        
        # Calculate card NPY with proper annualization
        net_card_revenue = total_card_revenue - total_card_costs
        card_net_portfolio_yield = (net_card_revenue / total_card_balance) * (365 / avg_period_days) if total_card_balance > 0 else 0
        
        return {
            'card_net_portfolio_yield': card_net_portfolio_yield,
            'total_card_revenue': total_card_revenue,
            'total_card_costs': total_card_costs,
            'net_card_revenue': net_card_revenue,
            'total_card_balance': total_card_balance,
            'card_cost_ratio': (total_card_costs / total_card_revenue * 100) if total_card_revenue > 0 else 0,
            'avg_period_days': avg_period_days,
            'annualization_factor': 365 / avg_period_days
        }
    
    def calculate_all_yield_metrics(self, filter_active: bool = True) -> Dict:
        """
        Calculate all yield metrics using industry-standard approach.
        
        Returns:
            Dictionary with all yield metrics
        """
        return {
            'gross_portfolio_yield': self.calculate_gross_portfolio_yield(filter_active),
            'net_portfolio_yield': self.calculate_net_portfolio_yield(filter_active),
            'net_portfolio_yield_after_coc': self.calculate_net_portfolio_yield_after_cost_of_capital(filter_active),
            'line_gross_portfolio_yield': self.calculate_line_gross_portfolio_yield(filter_active),
            'card_gross_portfolio_yield': self.calculate_card_gross_portfolio_yield(filter_active),
            'card_net_portfolio_yield': self.calculate_card_net_portfolio_yield(filter_active)
        }
    
    def get_data_summary(self) -> Dict:
        """Get summary of data used in calculations."""
        status_counts = self.data['accountEndingStatus'].value_counts()
        
        return {
            'total_records': len(self.data),
            'unique_businesses': self.data['businessGuid'].nunique(),
            'unique_accounts': self.data['capitalAccountGuid'].nunique(),
            'account_statuses': status_counts.to_dict(),
            'date_range': {
                'min_date': self.data['snapshotEndingAt'].min(),
                'max_date': self.data['snapshotEndingAt'].max()
            }
        }


class BusinessMetricsCalculator:
    """Calculate business-level metrics by vintage."""
    
    @staticmethod
    def calculate_business_metrics(data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate business-level metrics grouped by business and monthly vintage.
        
        Args:
            data: Preprocessed loan tape data
            
        Returns:
            DataFrame with business metrics by business and vintage
        """
        # Create a copy to avoid modifying original data
        df = data.copy()
        
        # Calculate vintage month (month when account was activated)
        df['vintage_month'] = df['accountActivatedAt'].dt.to_period('M')
        
        # Calculate account age in months
        df['accountAge'] = ((df['snapshotEndingAt'] - df['accountActivatedAt']).dt.days / 30.44).round(1)
        
        # Calculate revenue (interest + interchange)
        df['revenue'] = df['lineFeesAccrued'] + df['cardNetInterchangeAccrued']
        
        # Calculate APR (annualized rate)
        df['apr'] = (df['lineFeesAccrued'] / df['accountDailyAveragePrincipalBalance'] * 365 / 30.44 * 100).round(2)
        
        # Get priority status
        df['status'] = df['accountEndingStatus'].apply(BusinessMetricsCalculator._get_priority_status)
        
        # Add limit column (using balance as proxy since limit not in data)
        df['limit'] = df['accountDailyAveragePrincipalBalance'] * 1.2  # Estimate limit as 120% of balance
        
        # Group by business and vintage month, then aggregate metrics
        business_vintage_metrics = df.groupby(['businessGuid', 'vintage_month']).agg({
            'limit': 'sum',
            'accountDailyAveragePrincipalBalance': 'sum',
            'accountAge': 'mean',
            'revenue': 'sum',
            'apr': 'mean',
            'status': lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'Unknown',
            'capitalAccountGuid': 'count',
            'accountType': lambda x: ', '.join(x.unique())  # Show all account types
        }).reset_index()
        
        # Rename columns for clarity
        business_vintage_metrics.columns = [
            'businessGuid',
            'vintage_month',
            'totalLimit',
            'totalAverageDailyBalance',
            'avgAccountAge',
            'totalRevenue',
            'avgAPR',
            'primaryStatus',
            'accountCount',
            'accountTypes'
        ]
        
        # Add business identifier (shortened for display)
        business_vintage_metrics['businessId'] = business_vintage_metrics['businessGuid'].str[:8] + '...'
        
        # Sort by business, status priority, vintage month (newest first)
        # Status priority: "Closed" > "Current" > "Delinquent" > "Default" > "ChargedOff"
        status_priority = {
            'Closed': 1,
            'Current': 2,
            'Delinquent': 3,
            'Default': 4,
            'ChargedOff': 5
        }
        
        # Add status priority for sorting
        business_vintage_metrics['status_priority'] = business_vintage_metrics['primaryStatus'].map(status_priority)
        
        business_vintage_metrics = business_vintage_metrics.sort_values(
            ['businessGuid', 'status_priority', 'vintage_month'], 
            ascending=[True, True, False]
        )
        
        # Remove the temporary status_priority column
        business_vintage_metrics = business_vintage_metrics.drop('status_priority', axis=1)
        
        return business_vintage_metrics
    
    @staticmethod
    def _get_priority_status(status: str) -> str:
        """
        Get priority status based on specified order.
        Priority: "Closed" > "Current" > "Delinquent" > "Default" > "ChargedOff"
        
        Args:
            status: Account status
            
        Returns:
            Priority status
        """
        priority_order = {
            'Closed': 1,
            'Current': 2,
            'Delinquent': 3,
            'Default': 4,
            'ChargedOff': 5
        }
        
        return status if status in priority_order else 'Unknown' 