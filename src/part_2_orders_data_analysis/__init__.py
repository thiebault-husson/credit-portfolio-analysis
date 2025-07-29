"""
Part 2: Orders Data Analysis Package

This package contains modules for analyzing orders and customer data including
lifetime value, average order value, customer acquisition cost, and insights generation.
"""

from .orders_data_analyzer import OrdersAnalyzer
from .orders_data_processor import OrdersDataProcessor

__all__ = [
    'OrdersAnalyzer',
    'OrdersDataProcessor'
] 