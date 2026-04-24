"""Data models for the accounting application.

This module defines data structures used across the application,
particularly for transaction tracking and history.
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any


@dataclass
class Transaction:
    """Represents a single account transaction.
    
    Attributes:
        timestamp: ISO format timestamp of when transaction occurred
        type: Transaction type ('credit' or 'debit')
        amount: Transaction amount
        balance_before: Account balance before transaction
        balance_after: Account balance after transaction
    """
    timestamp: str
    type: str
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary for JSON serialization.
        
        Returns:
            Dictionary with string values for Decimal fields
        """
        return {
            'timestamp': self.timestamp,
            'type': self.type,
            'amount': str(self.amount),
            'balance_before': str(self.balance_before),
            'balance_after': str(self.balance_after)
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Transaction':
        """Create Transaction from dictionary.
        
        Args:
            data: Dictionary containing transaction data
            
        Returns:
            Transaction instance
        """
        return Transaction(
            timestamp=data['timestamp'],
            type=data['type'],
            amount=Decimal(data['amount']),
            balance_before=Decimal(data['balance_before']),
            balance_after=Decimal(data['balance_after'])
        )
    
    @staticmethod
    def create(type: str, amount: Decimal, balance_before: Decimal, 
               balance_after: Decimal) -> 'Transaction':
        """Create a new transaction with current timestamp.
        
        Args:
            type: Transaction type ('credit' or 'debit')
            amount: Transaction amount
            balance_before: Balance before transaction
            balance_after: Balance after transaction
            
        Returns:
            New Transaction instance with current timestamp
        """
        timestamp = datetime.now().isoformat()
        return Transaction(timestamp, type, amount, balance_before, balance_after)
