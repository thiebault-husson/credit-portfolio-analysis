"""
Orders analysis module for Part 2 of the case study.
"""

import pandas as pd
import json
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .orders_data_processor import OrdersDataProcessor


class OrdersAnalyzer:
    """Main class for orders analysis (Part 2)."""
    
    def __init__(self, orders_path: str, bank_transactions_path: str):
        """
        Initialize the orders analyzer.
        
        Args:
            orders_path: Path to the orders CSV file
            bank_transactions_path: Path to the bank transactions CSV file
        """
        self.orders_path = orders_path
        self.bank_transactions_path = bank_transactions_path
        self._orders_data = None
        self._bank_transactions = None
        self._cohort_analysis = None
        self._global_ltv = None
        self._global_aov = None
        self._global_cac = None
    
    @property
    def orders_data(self) -> pd.DataFrame:
        """Lazy load orders data."""
        if self._orders_data is None:
            self._orders_data = OrdersDataProcessor.load_orders_data(self.orders_path)
        return self._orders_data
    
    @property
    def bank_transactions(self) -> pd.DataFrame:
        """Lazy load bank transactions data."""
        if self._bank_transactions is None:
            self._bank_transactions = OrdersDataProcessor.load_bank_transactions(self.bank_transactions_path)
        return self._bank_transactions
    
    def analyze_orders(self) -> Dict:
        """
        Run complete orders analysis (Part 2).
        
        Returns:
            Dictionary with all Part 2 metrics and insights
        """
        # Calculate cohort metrics
        self._cohort_analysis = self._calculate_cohort_metrics()
        
        # Calculate LTV, AOV, CAC (both global and cohort-level)
        ltv_analysis = self._calculate_cohort_ltv()
        aov_analysis = self._calculate_cohort_aov()
        cac_analysis = self._calculate_cohort_cac()
        
        # Generate insights
        insights = self._generate_insights()
        
        # Get summary stats
        summary_stats = self.get_summary_stats()
        
        return {
            'cohort_metrics': self._cohort_analysis,
            'lifetime_value': ltv_analysis,
            'average_order_value': aov_analysis,
            'customer_acquisition_cost': cac_analysis,
            'insights': insights,
            'summary_stats': summary_stats
        }
    
    def _calculate_cohort_metrics(self) -> pd.DataFrame:
        """
        Calculate basic cohort metrics.
        
        Returns:
            DataFrame with cohort metrics
        """
        # Extract customer and first order date
        customer_cohorts = self.orders_data.groupby('customer').agg({
            'created_at': 'min',
            'order_id': 'count',
            'net_revenue': 'sum'  # Use net_revenue instead of total_amount
        }).reset_index()
        
        customer_cohorts.columns = ['customer', 'first_order_date', 'order_count', 'total_spent']
        
        # Add cohort month
        customer_cohorts['cohort_month'] = customer_cohorts['first_order_date'].dt.to_period('M')
        
        # Calculate cohort metrics
        cohort_metrics = customer_cohorts.groupby('cohort_month').agg({
            'customer': 'count',
            'order_count': 'sum',
            'total_spent': 'sum'
        }).reset_index()
        
        cohort_metrics.columns = ['cohort_month', 'customer_count', 'total_orders', 'total_revenue']
        cohort_metrics['average_orders_per_customer'] = cohort_metrics['total_orders'] / cohort_metrics['customer_count']
        cohort_metrics['average_revenue_per_customer'] = cohort_metrics['total_revenue'] / cohort_metrics['customer_count']
        
        # Add LTV columns for consistency with template
        cohort_metrics['total_ltv'] = cohort_metrics['total_revenue']
        cohort_metrics['avg_ltv'] = cohort_metrics['average_revenue_per_customer']
        
        # Add AOV columns for consistency with template
        cohort_metrics['order_count'] = cohort_metrics['total_orders']
        cohort_metrics['avg_aov'] = cohort_metrics['total_revenue'] / cohort_metrics['total_orders']
        
        return cohort_metrics
    
    def _calculate_global_ltv(self) -> Dict:
        """
        Calculate global lifetime value metrics from clean orders data (cached).
        
        Returns:
            Dictionary with global LTV metrics
        """
        if self._global_ltv is None:
            # Calculate global metrics directly from orders data
            total_revenue = self.orders_data['net_revenue'].sum()
            total_customers = self.orders_data['customer'].nunique()
            global_ltv = total_revenue / total_customers if total_customers > 0 else 0
            
            # Calculate customer-level LTV for median
            customer_ltv = self.orders_data.groupby('customer')['net_revenue'].sum()
            
            self._global_ltv = {
                'average_ltv': global_ltv,
                'median_ltv': customer_ltv.median(),
                'total_customers': total_customers,
                'total_revenue': total_revenue
            }
        
        return self._global_ltv
    
    def _calculate_cohort_ltv(self) -> Dict:
        """
        Calculate lifetime value by monthly cohort.
        
        Returns:
            Dictionary with cohort-level LTV analysis
        """
        if self._cohort_analysis is None:
            self._cohort_analysis = self._calculate_cohort_metrics()
        
        ltv_data = self._cohort_analysis.copy()
        ltv_data['ltv'] = ltv_data['average_revenue_per_customer']
        
        return {
            'by_cohort': ltv_data[['cohort_month', 'customer_count', 'ltv']].to_dict('records'),
            'summary': self._calculate_global_ltv()
        }
    
    def _calculate_global_aov(self) -> Dict:
        """
        Calculate global average order value metrics from clean orders data (cached).
        
        Returns:
            Dictionary with global AOV metrics
        """
        if self._global_aov is None:
            # Calculate global metrics directly from orders data
            total_revenue = self.orders_data['net_revenue'].sum()
            total_orders = len(self.orders_data)
            global_aov = total_revenue / total_orders if total_orders > 0 else 0
            
            self._global_aov = {
                'average_aov': global_aov,
                'median_aov': self.orders_data['net_revenue'].median(),
                'total_orders': total_orders,
                'total_revenue': total_revenue
            }
        
        return self._global_aov
    
    def _calculate_cohort_aov(self) -> Dict:
        """
        Calculate average order value by monthly cohort.
        
        Returns:
            Dictionary with cohort-level AOV analysis
        """
        if self._cohort_analysis is None:
            self._cohort_analysis = self._calculate_cohort_metrics()
        
        aov_data = self._cohort_analysis.copy()
        aov_data['aov'] = aov_data['total_revenue'] / aov_data['total_orders']
        
        return {
            'by_cohort': aov_data[['cohort_month', 'customer_count', 'aov']].to_dict('records'),
            'summary': self._calculate_global_aov()
        }
    
    def _calculate_global_cac(self) -> Dict:
        """
        Calculate global customer acquisition cost (cached).
        
        Returns:
            Dictionary with global CAC metrics
        """
        if self._global_cac is None:
            # Estimate CAC based on bank transactions (marketing spend)
            marketing_spend = self.bank_transactions[
                self.bank_transactions['category'].str.contains('Marketing', na=False)
            ]['amount'].sum()
            
            total_customers = self.orders_data['customer'].nunique()
            estimated_cac = abs(marketing_spend) / total_customers if total_customers > 0 else 0
            
            # Calculate LTV/CAC ratio using global LTV
            global_ltv = self._calculate_global_ltv()['average_ltv']
            ltv_cac_ratio = global_ltv / estimated_cac if estimated_cac > 0 else 0
            
            self._global_cac = {
                'estimated_cac': estimated_cac,
                'total_marketing_spend': abs(marketing_spend),
                'total_customers': total_customers,
                'ltv_cac_ratio': ltv_cac_ratio
            }
        
        return self._global_cac
    
    def _calculate_cohort_cac(self) -> Dict:
        """
        Calculate customer acquisition cost by monthly cohort.
        
        Returns:
            Dictionary with cohort-level CAC analysis
        """
        if self._cohort_analysis is None:
            self._cohort_analysis = self._calculate_cohort_metrics()
        
        # Calculate marketing spend by month
        bank_transactions = self.bank_transactions.copy()
        bank_transactions['month'] = pd.to_datetime(bank_transactions['date']).dt.to_period('M')
        
        # Filter for marketing transactions
        marketing_transactions = bank_transactions[
            bank_transactions['category'].str.contains('Marketing', na=False)
        ]
        
        # Calculate marketing spend by month
        monthly_marketing_spend = marketing_transactions.groupby('month')['amount'].sum().abs()
        
        # Get cohort data
        cac_data = self._cohort_analysis.copy()
        
        # Calculate CAC for each cohort
        cac_data['marketing_spend'] = cac_data['cohort_month'].map(monthly_marketing_spend).fillna(0)
        cac_data['cac'] = cac_data['marketing_spend'] / cac_data['customer_count']
        cac_data['cac'] = cac_data['cac'].fillna(0)  # Handle division by zero
        
        return {
            'by_cohort': cac_data[['cohort_month', 'customer_count', 'marketing_spend', 'cac']].to_dict('records'),
            'summary': self._calculate_global_cac()
        }
    
    def _generate_insights(self) -> Dict:
        """
        Generate insights from the orders data.
        
        Returns:
            Dictionary with key insights
        """
        insights = {}
        
        # Customer behavior insights
        customer_behavior = self.orders_data.groupby('customer').agg({
            'order_id': 'count',
            'net_revenue': 'sum',  # Use net_revenue instead of total_amount
            'created_at': ['min', 'max']
        }).reset_index()
        
        customer_behavior.columns = ['customer', 'order_count', 'total_spent', 'first_order', 'last_order']
        customer_behavior['customer_lifetime_days'] = (
            customer_behavior['last_order'] - customer_behavior['first_order']
        ).dt.days
        
        insights['customer_behavior'] = {
            'total_customers': len(customer_behavior),
            'average_orders_per_customer': customer_behavior['order_count'].mean(),
            'average_customer_lifetime_days': customer_behavior['customer_lifetime_days'].mean(),
            'repeat_customers': len(customer_behavior[customer_behavior['order_count'] > 1]),
            'repeat_customer_rate': len(customer_behavior[customer_behavior['order_count'] > 1]) / len(customer_behavior)
        }
        
        # Revenue insights (using net revenue)
        revenue_analysis = self.orders_data.groupby(
            self.orders_data['created_at'].dt.to_period('M')
        ).agg({
            'order_id': 'count',
            'net_revenue': 'sum'  # Use net_revenue instead of total_amount
        }).reset_index()
        
        revenue_analysis.columns = ['month', 'order_count', 'revenue']
        
        insights['revenue_trends'] = {
            'total_revenue': revenue_analysis['revenue'].sum(),
            'average_monthly_revenue': revenue_analysis['revenue'].mean(),
            'revenue_growth_trend': 'increasing' if len(revenue_analysis) > 1 and 
                revenue_analysis['revenue'].iloc[-1] > revenue_analysis['revenue'].iloc[0] else 'stable',
            'peak_month': revenue_analysis.loc[revenue_analysis['revenue'].idxmax(), 'month'] if not revenue_analysis.empty else None
        }
        
        # Add refund and discount insights
        total_gross = self.orders_data['gross_amount'].sum()
        total_refunds = self.orders_data['refunds'].sum()
        total_discounts = self.orders_data['discounts'].sum()
        total_net = self.orders_data['net_revenue'].sum()
        
        insights['revenue_breakdown'] = {
            'gross_revenue': total_gross,
            'total_refunds': total_refunds,
            'total_discounts': total_discounts,
            'net_revenue': total_net,
            'refund_rate': (total_refunds / total_gross * 100) if total_gross > 0 else 0,
            'discount_rate': (total_discounts / total_gross * 100) if total_gross > 0 else 0
        }
        
        # Geographic insights
        if 'location' in self.orders_data.columns:
            # Handle location data that's already parsed as dict
            countries = []
            for location in self.orders_data['location']:
                if isinstance(location, dict) and 'country' in location:
                    countries.append(location.get('country', 'Unknown'))
                else:
                    countries.append('Unknown')
            
            insights['geographic_distribution'] = pd.Series(countries).value_counts().to_dict()
        
        return insights
    
    def get_summary_stats(self) -> Dict:
        """
        Get summary statistics for the orders data.
        
        Returns:
            Dictionary with summary statistics
        """
        # Calculate average LTV
        customer_ltv = self.orders_data.groupby('customer')['net_revenue'].sum()
        average_ltv = customer_ltv.mean() if len(customer_ltv) > 0 else 0
        
        # Calculate average AOV
        average_aov = self.orders_data['net_revenue'].mean()
        
        # Calculate average orders per customer
        customer_orders = self.orders_data.groupby('customer')['order_id'].count()
        avg_orders_per_customer = customer_orders.mean()
        
        # Get CAC metrics
        cac_metrics = self._calculate_global_cac()
        
        # Get cohort metrics for number of cohorts
        cohort_metrics = self._calculate_cohort_metrics()
        number_of_cohorts = len(cohort_metrics) if not cohort_metrics.empty else 0
        
        return {
            'total_orders': len(self.orders_data),
            'total_customers': self.orders_data['customer'].nunique(),
            'average_ltv': average_ltv,
            'average_aov': average_aov,
            'avg_orders_per_customer': avg_orders_per_customer,
            'date_range': {
                'start': self.orders_data['created_at'].min(),
                'end': self.orders_data['created_at'].max()
            },
            'gross_revenue': self.orders_data['gross_amount'].sum(),
            'net_revenue': self.orders_data['net_revenue'].sum(),
            'total_revenue': self.orders_data['net_revenue'].sum(),  # Add total_revenue for template compatibility
            'total_refunds': self.orders_data['refunds'].sum(),
            'total_discounts': self.orders_data['discounts'].sum(),
            'average_order_value': self.orders_data['net_revenue'].mean(),
            'bank_transactions_count': len(self.bank_transactions),
            'bank_transactions_categories': self.bank_transactions['category'].nunique(),
            # CAC metrics
            'average_cac': cac_metrics['estimated_cac'],
            'total_marketing_spend': cac_metrics['total_marketing_spend'],
            'ltv_cac_ratio': cac_metrics['ltv_cac_ratio'],
            # Cohort metrics
            'number_of_cohorts': number_of_cohorts
        } 