"""
Data processor for Part 2 orders and bank transactions data.
"""

import pandas as pd
import json
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from functools import lru_cache


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
        
        # Convert date columns with robust parsing
        date_columns = ['created_at', 'updated_at', 'cancelled_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = OrdersDataProcessor._robust_parse_dates(df, col)
        
        # Extract total amount from line_items JSON
        df['gross_amount'] = df['line_items'].apply(OrdersDataProcessor._extract_total_amount)
        
        # Parse refunds and discounts with correct field names
        df['refunds'] = df['refunds'].apply(OrdersDataProcessor._parse_refunds)
        df['discounts'] = df['discounts'].apply(OrdersDataProcessor._parse_discounts)
        
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
    @lru_cache(maxsize=1024)
    def _extract_total_amount(line_items_str: str) -> float:
        """
        Extract total amount from line_items JSON string (cached).
        
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
    @lru_cache(maxsize=1024)
    def _parse_refunds(value: str) -> float:
        """
        Parse refunds value - uses 'shop_amount' or 'presentment_amount'.
        
        Args:
            value: String value from refunds column
            
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
                elif isinstance(parsed, dict):
                    # For refunds: prefer shop_amount or presentment_amount
                    if 'shop_amount' in parsed:
                        return float(parsed['shop_amount'])
                    elif 'presentment_amount' in parsed:
                        return float(parsed['presentment_amount'])
                    elif 'amount' in parsed:
                        return float(parsed['amount'])
                elif isinstance(parsed, list) and len(parsed) > 0:
                    # Handle list of refunds
                    total = 0.0
                    for item in parsed:
                        if isinstance(item, dict):
                            if 'shop_amount' in item:
                                total += float(item['shop_amount'])
                            elif 'presentment_amount' in item:
                                total += float(item['presentment_amount'])
                            elif 'amount' in item:
                                total += float(item['amount'])
                    return total
                else:
                    return 0.0
            except (json.JSONDecodeError, TypeError):
                # If not JSON, try to parse as numeric string
                return float(value) if value.replace('.', '').replace('-', '').isdigit() else 0.0
                
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    @lru_cache(maxsize=1024)
    def _parse_discounts(value: str) -> float:
        """
        Parse discounts value - uses 'amount' field.
        
        Args:
            value: String value from discounts column
            
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
                elif isinstance(parsed, dict):
                    # For discounts: prefer 'amount' field
                    if 'amount' in parsed:
                        return float(parsed['amount'])
                    elif 'shop_amount' in parsed:
                        return float(parsed['shop_amount'])
                    elif 'presentment_amount' in parsed:
                        return float(parsed['presentment_amount'])
                elif isinstance(parsed, list) and len(parsed) > 0:
                    # Handle list of discounts
                    total = 0.0
                    for item in parsed:
                        if isinstance(item, dict):
                            if 'amount' in item:
                                total += float(item['amount'])
                            elif 'shop_amount' in item:
                                total += float(item['shop_amount'])
                            elif 'presentment_amount' in item:
                                total += float(item['presentment_amount'])
                    return total
                else:
                    return 0.0
            except (json.JSONDecodeError, TypeError):
                # If not JSON, try to parse as numeric string
                return float(value) if value.replace('.', '').replace('-', '').isdigit() else 0.0
                
        except (ValueError, TypeError):
            return 0.0
    
    @staticmethod
    def _robust_parse_dates(df: pd.DataFrame, column: str) -> pd.Series:
        """
        Parse dates robustly using optimized chunked processing.
        
        Args:
            df: DataFrame containing the data
            column: Name of the date column to parse
            
        Returns:
            Parsed dates as pandas Series
        """
        # Try bulk parsing first (most efficient)
        try:
            result = pd.to_datetime(df[column], format='mixed', utc=True)
            return result.dt.tz_localize(None)
        except Exception:
            # Fallback to chunked processing only if bulk fails
            result = pd.Series(index=df.index, dtype='datetime64[ns]')
            chunk_size = 2000  # Increased chunk size for better performance
            
            for i in range(0, len(df), chunk_size):
                chunk = df.iloc[i:i+chunk_size]
                
                try:
                    chunk_dates = pd.to_datetime(chunk[column], format='mixed', utc=True)
                    chunk_dates = chunk_dates.dt.tz_localize(None)
                    result.iloc[i:i+len(chunk)] = chunk_dates
                except Exception:
                    # Individual parsing only for problematic chunks
                    for j, date_str in enumerate(chunk[column]):
                        try:
                            if pd.isna(date_str) or date_str == '':
                                result.iloc[i+j] = pd.NaT
                            else:
                                # Try formats in order of likelihood
                                for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S']:
                                    try:
                                        result.iloc[i+j] = pd.to_datetime(date_str, format=fmt)
                                        break
                                    except:
                                        continue
                                else:
                                    try:
                                        parsed_date = pd.to_datetime(date_str, utc=True)
                                        result.iloc[i+j] = parsed_date.tz_localize(None) if parsed_date.tz is not None else parsed_date
                                    except:
                                        result.iloc[i+j] = pd.NaT
                        except:
                            result.iloc[i+j] = pd.NaT
            
            return result

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