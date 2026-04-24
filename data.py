"""Concrete implementation of the data layer with JSON persistence.

This module implements the AccountDataInterface using JSON file storage,
providing persistent storage of the account balance across program runs.
"""

import json
import logging
from decimal import Decimal
from pathlib import Path
from typing import List, Dict, Optional

from constants import DATA_FILE, INITIAL_BALANCE, ZERO
from data_interface import AccountDataInterface
from exceptions import DataPersistenceError
from models import Transaction


logger = logging.getLogger(__name__)


class AccountData(AccountDataInterface):
    """Concrete implementation of account data storage using JSON files.
    
    This class stores the account balance in a JSON file, providing
    persistence across program restarts. It handles file creation,
    corruption recovery, and graceful error handling.
    """
    
    def __init__(self, data_file: Path = DATA_FILE) -> None:
        """Initialize the data store and load existing balance if available.
        
        Args:
            data_file: Path to the JSON file for storing the balance
        """
        self._data_file = data_file
        self._balance: Decimal = INITIAL_BALANCE
        self._transactions: List[Transaction] = []
        self._load()
    
    def read_balance(self) -> Decimal:
        """Read the current account balance.
        
        Returns:
            The current balance as a Decimal
        """
        return self._balance
    
    def write_balance(self, amount: Decimal, transaction_type: Optional[str] = None, 
                     transaction_amount: Optional[Decimal] = None) -> None:
        """Write a new account balance and persist to disk.
        
        Args:
            amount: The new balance to store
            transaction_type: Type of transaction ('credit' or 'debit'), None for direct set
            transaction_amount: Amount of the transaction
            
        Raises:
            DataPersistenceError: If the balance cannot be saved to disk
        """
        # Validate amount is a Decimal
        if not isinstance(amount, Decimal):
            raise ValueError(f"Balance must be a Decimal, got {type(amount)}")
        
        # Record transaction if type is provided
        if transaction_type and transaction_amount:
            transaction = Transaction.create(
                type=transaction_type,
                amount=transaction_amount,
                balance_before=self._balance,
                balance_after=amount
            )
            self._transactions.append(transaction)
        
        self._balance = amount
        self._persist()
    
    def _persist(self) -> None:
        """Save the current balance to the JSON file.
        
        Raises:
            DataPersistenceError: If the file cannot be written
        """
        try:
            # Ensure parent directory exists
            self._data_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write balance and transactions to file
            data = {
                'balance': str(self._balance),
                'transactions': [txn.to_dict() for txn in self._transactions]
            }
            with self._data_file.open('w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            logger.debug(f"Balance persisted: {self._balance}")
            
        except (IOError, OSError) as e:
            error_msg = f"Failed to persist balance to {self._data_file}: {e}"
            logger.error(error_msg)
            raise DataPersistenceError(error_msg) from e
    
    def _load(self) -> None:
        """Load the balance from the JSON file.
        
        If the file doesn't exist or is corrupted, initializes with
        the default INITIAL_BALANCE and creates the file.
        """
        if not self._data_file.exists():
            logger.info(
                f"Data file {self._data_file} not found. "
                f"Creating with initial balance: {INITIAL_BALANCE}"
            )
            self._balance = INITIAL_BALANCE
            self._persist()
            return
        
        try:
            with self._data_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract and validate balance
            balance_str = data['balance']
            balance = Decimal(balance_str)
            
            # Load transactions if present
            if 'transactions' in data:
                self._transactions = [
                    Transaction.from_dict(txn) for txn in data['transactions']
                ]
            else:
                self._transactions = []
            
            # Validate balance is positive
            if balance < 0:
                logger.warning(
                    f"Loaded balance is negative ({balance}). "
                    f"Resetting to {INITIAL_BALANCE}"
                )
                self._balance = INITIAL_BALANCE
                self._transactions = []
                self._persist()
            else:
                self._balance = balance
                logger.debug(f"Loaded balance: {self._balance} with {len(self._transactions)} transactions")
                
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(
                f"Corrupted data file {self._data_file}: {e}. "
                f"Resetting to initial balance: {INITIAL_BALANCE}"
            )
            self._balance = INITIAL_BALANCE
            self._transactions = []
            self._persist()
        except (IOError, OSError) as e:
            logger.error(f"Failed to read data file {self._data_file}: {e}")
            # Continue with INITIAL_BALANCE, don't crash
            self._balance = INITIAL_BALANCE
            self._transactions = []
    
    def get_transactions(self, limit: Optional[int] = None) -> List[Transaction]:
        """Get transaction history, most recent first.
        
        Args:
            limit: Maximum number of transactions to return, None for all
            
        Returns:
            List of Transaction objects in reverse chronological order
        """
        transactions = list(reversed(self._transactions))
        if limit:
            return transactions[:limit]
        return transactions
    
    def get_transaction_stats(self) -> Dict[str, Decimal]:
        """Calculate statistics about transactions.
        
        Returns:
            Dictionary with total_credits, total_debits, net_change, count
        """
        total_credits = ZERO
        total_debits = ZERO
        
        for txn in self._transactions:
            if txn.type == 'credit':
                total_credits += txn.amount
            elif txn.type == 'debit':
                total_debits += txn.amount
        
        return {
            'total_credits': total_credits,
            'total_debits': total_debits,
            'net_change': total_credits - total_debits,
            'count': len(self._transactions)
        }
