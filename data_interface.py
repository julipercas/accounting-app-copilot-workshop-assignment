"""Abstract interface for the data layer.

This module defines the contract that all data storage implementations
must follow, enabling the Dependency Inversion Principle (SOLID).
"""

from abc import ABC, abstractmethod
from decimal import Decimal


class AccountDataInterface(ABC):
    """Abstract base class for account data storage.
    
    This interface defines the contract for data layer implementations,
    allowing the business logic layer to depend on abstractions rather
    than concrete implementations. This enables easy swapping of storage
    backends (e.g., JSON file, SQLite, PostgreSQL) without changing
    business logic.
    """
    
    @abstractmethod
    def read_balance(self) -> Decimal:
        """Read the current account balance.
        
        Returns:
            The current balance as a Decimal
        """
        pass
    
    @abstractmethod
    def write_balance(self, amount: Decimal) -> None:
        """Write a new account balance.
        
        Args:
            amount: The new balance to store
            
        Raises:
            DataPersistenceError: If the balance cannot be saved
        """
        pass
