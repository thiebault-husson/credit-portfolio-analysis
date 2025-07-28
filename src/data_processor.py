"""
Data processing utilities for loan tape analysis.
"""

import pandas as pd
import re
from typing import Optional
from datetime import datetime


class LoanDataProcessor:
    """Handle data loading and preprocessing for loan tape analysis."""
    
    @staticmethod
    def load_loan_tape(file_path: str) -> pd.DataFrame:
        """
        Load and preprocess loan tape CSV file.
        
        Args:
            file_path: Path to the loan tape CSV file
            
        Returns:
            Preprocessed DataFrame with proper data types
        """
        # Load the CSV file
        df = pd.read_csv(file_path)
        
        # Preprocess the data
        df = LoanDataProcessor._preprocess_data(df)
        
        return df
    
    @staticmethod
    def _preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the loan tape data.
        
        Args:
            df: Raw loan tape DataFrame
            
        Returns:
            Preprocessed DataFrame
        """
        # Convert date columns
        date_columns = [
            'snapshotBeginningAt', 'snapshotEndingAt', 
            'accountActivatedAt', 'accountDefaultedAt', 
            'accountTerminatedAt', 'accountDelinquentAt',
            'lineOldestUnpaidOriginationAt'
        ]
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Parse currency columns
        currency_columns = [
            'accountEndingLimit', 'accountDailyAveragePrincipalBalance',
            'lineBeginningPrincipalBalance', 'lineBeginningFeesBalance',
            'linePrincipalOriginated', 'linePrincipalRepaymentsPaid',
            'lineFeesAccrued', 'lineFeesPaid', 'lineEndingFeesBalance',
            'lineEndingPrincipalBalance', 'lineDailyAveragePrincipalBalance',
            'cardBeginningPrincipalBalance', 'cardPrincipalOriginated',
            'cardPrincipalRepaymentsPaid', 'cardNetInterchangeAccrued',
            'cardRewardsAccrued', 'cardEndingPrincipalBalance',
            'cardDailyAveragePrincipalBalance'
        ]
        
        for col in currency_columns:
            if col in df.columns:
                df[col] = df[col].apply(LoanDataProcessor.parse_currency)
        
        # Parse percentage columns
        percentage_columns = [
            'linePaymentRate', 'lineEndingApr', 'accountPaymentRate'
        ]
        
        for col in percentage_columns:
            if col in df.columns:
                df[col] = df[col].apply(LoanDataProcessor.parse_percentage)
        
        # Convert numeric columns
        numeric_columns = ['lineEndingTargetRepaymentDays']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    @staticmethod
    def parse_currency(value: str) -> float:
        """
        Parse currency string to float.
        
        Args:
            value: Currency string like "$750,000.00"
            
        Returns:
            Float value
        """
        if pd.isna(value) or value == '':
            return 0.0
        
        # Remove $ and commas, convert to float
        cleaned = str(value).replace('$', '').replace(',', '')
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    @staticmethod
    def parse_percentage(value: str) -> float:
        """
        Parse percentage string to float.
        
        Args:
            value: Percentage string like "5.09%"
            
        Returns:
            Float value (as decimal, e.g., 0.0509 for 5.09%)
        """
        if pd.isna(value) or value == '':
            return 0.0
        
        # Remove % and convert to decimal
        cleaned = str(value).replace('%', '')
        try:
            return float(cleaned) / 100
        except ValueError:
            return 0.0
    
    @staticmethod
    def get_month_from_date(date_col: str) -> str:
        """
        Extract month string from date column.
        
        Args:
            date_col: Date column name
            
        Returns:
            Month string in 'YYYY-MM' format
        """
        if pd.isna(date_col):
            return None
        return date_col.strftime('%Y-%m') 