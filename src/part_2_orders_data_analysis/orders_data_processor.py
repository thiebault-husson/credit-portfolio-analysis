"""
Data processor for Part 2 orders and bank transactions data.
"""

import pandas as pd
import json
from typing import Dict, Any
from datetime import datetime


class OrdersDataProcessor:
    """Process orders and bank transactions data for Part 2 analysis."""
    
    @staticmethod
    def load_orders_data(file_path: str) -> pd.DataFrame:
        """
        Load and preprocess orders data.
        
        Args:
            file_path: Path to the orders CSV file
            
        Returns:
            Preprocessed orders DataFrame
        """
        # Load the data
        df = pd.read_csv(file_path)
        
        # Convert date columns
        date_columns = ['created_at', 'updated_at', 'cancelled_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Extract total amount from line_items JSON
        df['gross_amount'] = df['line_items'].apply(OrdersDataProcessor._extract_total_amount)
        
        # Parse refunds and discounts
        df['refunds'] = df['refunds'].apply(OrdersDataProcessor._parse_refunds_discounts)
        df['discounts'] = df['discounts'].apply(OrdersDataProcessor._parse_refunds_discounts)
        
        # Calculate net revenue (gross - refunds - discounts)
        df['net_revenue'] = df['gross_amount'] - df['refunds'] - df['discounts']
        
        # Extract location data
        df['location'] = df['line_items'].apply(OrdersDataProcessor._extract_location)
        
        return df
    
    @staticmethod
    def load_bank_transactions(file_path: str) -> pd.DataFrame:
        """
        Load and preprocess bank transactions data.
        
        Args:
            file_path: Path to the bank transactions CSV file
            
        Returns:
            Preprocessed bank transactions DataFrame
        """
        # Load the data
        df = pd.read_csv(file_path)
        
        # Convert date column
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Convert amount to numeric
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
        
        return df
    
    @staticmethod
    def _extract_total_amount(line_items_str: str) -> float:
        """
        Extract total amount from line_items JSON string.
        
        Args:
            line_items_str: JSON string containing line items
            
        Returns:
            Total amount as float
        """
        try:
            if pd.isna(line_items_str):
                return 0.0
            
            line_items = json.loads(line_items_str)
            total = 0.0
            
            for item in line_items:
                if isinstance(item, dict) and 'price_set' in item:
                    price_set = item['price_set']
                    if isinstance(price_set, dict) and 'shop_amount' in price_set:
                        total += float(price_set['shop_amount'])
            
            return total
        except (json.JSONDecodeError, ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def _parse_refunds_discounts(value: str) -> float:
        """
        Parse refunds or discounts value.
        
        Args:
            value: String value from refunds or discounts column
            
        Returns:
            Parsed amount as float
        """
        try:
            if pd.isna(value) or value == '':
                return 0.0
            
            # Try to parse as JSON first
            try:
                parsed = json.loads(value)
                if isinstance(parsed, (int, float)):
                    return float(parsed)
                elif isinstance(parsed, dict) and 'amount' in parsed:
                    return float(parsed['amount'])
                else:
                    return 0.0
            except (json.JSONDecodeError, TypeError):
                # If not JSON, try to parse as numeric string
                return float(value) if value.replace('.', '').replace('-', '').isdigit() else 0.0
                
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def _extract_location(line_items_str: str) -> Dict[str, Any]:
        """
        Extract location data from line_items JSON string.
        
        Args:
            line_items_str: JSON string containing line items
            
        Returns:
            Dictionary with location data
        """
        try:
            if pd.isna(line_items_str):
                return {}
            
            # Try to extract location from the JSON structure
            # The location data seems to be embedded in the line_items structure
            data = json.loads(line_items_str)
            
            # Look for location data in the structure
            if isinstance(data, dict) and 'location' in data:
                return data['location']
            elif isinstance(data, list) and len(data) > 0:
                # Check if first item has location info
                first_item = data[0]
                if isinstance(first_item, dict) and 'location' in first_item:
                    return first_item['location']
            
            return {}
        except (json.JSONDecodeError, ValueError, TypeError):
            return {}
    
    @staticmethod
    def parse_json_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
        """
        Parse JSON column in DataFrame.
        
        Args:
            df: DataFrame containing the column
            column: Name of the JSON column to parse
            
        Returns:
            DataFrame with parsed JSON column
        """
        if column not in df.columns:
            return df
        
        df[column] = df[column].apply(lambda x: json.loads(x) if pd.notna(x) and x != '' else {})
        return df 