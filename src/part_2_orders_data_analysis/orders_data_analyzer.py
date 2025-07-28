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
        self.orders_data = OrdersDataProcessor.load_orders_data(orders_path)
        self.bank_transactions = OrdersDataProcessor.load_bank_transactions(bank_transactions_path)
        self.cohort_analysis = None
    
    def analyze_orders(self) -> Dict:
        """
        Run complete orders analysis (Part 2).
        
        Returns:
            Dictionary with all Part 2 metrics and insights
        """
        # Calculate cohort metrics
        self.cohort_analysis = self._calculate_cohort_metrics()
        
        # Calculate LTV, AOV, CAC
        ltv_analysis = self._calculate_lifetime_value()
        aov_analysis = self._calculate_average_order_value()
        cac_analysis = self._calculate_customer_acquisition_cost()
        
        # Generate insights
        insights = self._generate_insights()
        
        return {
            'cohort_metrics': self.cohort_analysis,
            'lifetime_value': ltv_analysis,
            'average_order_value': aov_analysis,
            'customer_acquisition_cost': cac_analysis,
            'insights': insights
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
        
        return cohort_metrics
    
    def _calculate_lifetime_value(self) -> Dict:
        """
        Calculate lifetime value by monthly cohort.
        
        Returns:
            Dictionary with LTV analysis
        """
        if self.cohort_analysis is None:
            self.cohort_analysis = self._calculate_cohort_metrics()
        
        ltv_data = self.cohort_analysis.copy()
        ltv_data['ltv'] = ltv_data['average_revenue_per_customer']
        
        return {
            'by_cohort': ltv_data[['cohort_month', 'customer_count', 'ltv']].to_dict('records'),
            'summary': {
                'average_ltv': ltv_data['ltv'].mean(),
                'median_ltv': ltv_data['ltv'].median(),
                'total_customers': ltv_data['customer_count'].sum(),
                'total_ltv': ltv_data['ltv'].sum()
            }
        }
    
    def _calculate_average_order_value(self) -> Dict:
        """
        Calculate average order value by monthly cohort.
        
        Returns:
            Dictionary with AOV analysis
        """
        if self.cohort_analysis is None:
            self.cohort_analysis = self._calculate_cohort_metrics()
        
        aov_data = self.cohort_analysis.copy()
        aov_data['aov'] = aov_data['total_revenue'] / aov_data['total_orders']
        
        return {
            'by_cohort': aov_data[['cohort_month', 'customer_count', 'aov']].to_dict('records'),
            'summary': {
                'average_aov': aov_data['aov'].mean(),
                'median_aov': aov_data['aov'].median(),
                'total_orders': aov_data['total_orders'].sum(),
                'total_revenue': aov_data['total_revenue'].sum()
            }
        }
    
    def _calculate_customer_acquisition_cost(self) -> Dict:
        """
        Calculate customer acquisition cost by monthly cohort.
        
        Returns:
            Dictionary with CAC analysis
        """
        # This would typically use marketing spend data
        # For now, we'll estimate based on available data
        if self.cohort_analysis is None:
            self.cohort_analysis = self._calculate_cohort_metrics()
        
        # Estimate CAC based on bank transactions (marketing spend)
        marketing_spend = self.bank_transactions[
            self.bank_transactions['category'].str.contains('Marketing', na=False)
        ]['amount'].sum()
        
        total_customers = self.cohort_analysis['customer_count'].sum()
        estimated_cac = abs(marketing_spend) / total_customers if total_customers > 0 else 0
        
        cac_data = self.cohort_analysis.copy()
        cac_data['cac'] = estimated_cac  # Same CAC for all cohorts as estimate
        
        return {
            'by_cohort': cac_data[['cohort_month', 'customer_count', 'cac']].to_dict('records'),
            'summary': {
                'estimated_cac': estimated_cac,
                'total_marketing_spend': abs(marketing_spend),
                'total_customers': total_customers,
                'ltv_cac_ratio': self.cohort_analysis['average_revenue_per_customer'].mean() / estimated_cac if estimated_cac > 0 else 0
            }
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
        return {
            'total_orders': len(self.orders_data),
            'total_customers': self.orders_data['customer'].nunique(),
            'date_range': {
                'start': self.orders_data['created_at'].min(),
                'end': self.orders_data['created_at'].max()
            },
            'gross_revenue': self.orders_data['gross_amount'].sum(),
            'net_revenue': self.orders_data['net_revenue'].sum(),
            'total_refunds': self.orders_data['refunds'].sum(),
            'total_discounts': self.orders_data['discounts'].sum(),
            'average_order_value': self.orders_data['net_revenue'].mean(),
            'bank_transactions_count': len(self.bank_transactions),
            'bank_transactions_categories': self.bank_transactions['category'].nunique()
        } 