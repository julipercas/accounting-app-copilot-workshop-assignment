"""Business logic layer for account operations.

This module implements the core business logic for viewing balance,
crediting, and debiting the account. It follows the Single Responsibility
Principle by focusing solely on business rules.
"""

import logging
from decimal import Decimal
from typing import Tuple

from constants import OperationType, ZERO
from data_interface import AccountDataInterface
from exceptions import InsufficientFundsError, InvalidAmountError
from validators import validate_amount


logger = logging.getLogger(__name__)


class AccountOperations:
    """Handles all business logic for account operations.
    
    This class implements the business rules for viewing balance,
    crediting, and debiting accounts. It depends on the AccountDataInterface
    abstraction (Dependency Inversion Principle) rather than concrete
    implementations.
    
    Attributes:
        _data_store: The data storage implementation
    """
    
    def __init__(self, data_store: AccountDataInterface) -> None:
        """Initialize operations with a data store.
        
        Args:
            data_store: Implementation of AccountDataInterface for data access
        """
        self._data_store = data_store
    
    def view_balance(self) -> None:
        """Display the current account balance.
        
        Retrieves the balance from the data layer and displays it
        formatted as currency with 2 decimal places.
        """
        balance = self._data_store.read_balance()
        print(f"\nCurrent balance: ${balance:.2f}")
        logger.info(f"Balance viewed: {balance}")
    
    def credit_account(self, amount: Decimal) -> Tuple[bool, str]:
        """Add funds to the account (web-compatible version).
        
        Args:
            amount: Amount to credit (already validated)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Reject zero amounts
            if amount == ZERO:
                return (False, "Amount must be greater than zero")
            
            # Process transaction
            current_balance = self._data_store.read_balance()
            new_balance = current_balance + amount
            self._data_store.write_balance(new_balance, 'credit', amount)
            
            logger.info(f"Credit: {amount}, New balance: {new_balance}")
            return (True, f"Credit successful: ${amount:.2f}. New balance: ${new_balance:.2f}")
            
        except Exception as e:
            logger.error(f"Credit failed: {e}")
            return (False, f"Credit failed: {str(e)}")
    
    def debit_account(self, amount: Decimal) -> Tuple[bool, str]:
        """Withdraw funds from the account (web-compatible version).
        
        Args:
            amount: Amount to debit (already validated)
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Reject zero amounts
            if amount == ZERO:
                return (False, "Amount must be greater than zero")
            
            # Check sufficient funds
            current_balance = self._data_store.read_balance()
            if amount > current_balance:
                logger.warning(f"Insufficient funds: {amount} > {current_balance}")
                return (False, "Insufficient funds")
            
            # Process transaction
            new_balance = current_balance - amount
            self._data_store.write_balance(new_balance, 'debit', amount)
            
            logger.info(f"Debit: {amount}, New balance: {new_balance}")
            return (True, f"Debit successful: ${amount:.2f}. New balance: ${new_balance:.2f}")
            
        except Exception as e:
            logger.error(f"Debit failed: {e}")
            return (False, f"Debit failed: {str(e)}")
    
    def credit_account_cli(self) -> None:
        """Add funds to the account (CLI version with user input).
        
        Prompts the user for an amount, validates it, adds it to the
        current balance, and saves the new balance. Rejects zero amounts
        to match COBOL behavior (TC-2.2).
        """
        try:
            # Get and validate amount from user
            amount_str = input("\nEnter amount to credit: $")
            amount = validate_amount(amount_str)
            
            # Use the web-compatible method
            success, message = self.credit_account(amount)
            print(message)
            
        except InvalidAmountError as e:
            print(f"Invalid amount: {e}")
            logger.warning(f"Credit failed: {e}")
    
    def debit_account_cli(self) -> None:
        """Withdraw funds from the account (CLI version with user input).
        
        Prompts the user for an amount, validates it, checks for sufficient
        funds, subtracts from the current balance if valid, and saves the
        new balance. Displays an error if funds are insufficient.
        """
        try:
            # Get and validate amount from user
            amount_str = input("\nEnter amount to debit: $")
            amount = validate_amount(amount_str)
            
            # Use the web-compatible method
            success, message = self.debit_account(amount)
            print(message)
            
        except InvalidAmountError as e:
            print(f"Invalid amount: {e}")
            logger.warning(f"Debit failed: {e}")
    
    def handle_operation(self, operation: OperationType) -> None:
        """Route an operation to the appropriate handler method.
        
        Args:
            operation: The type of operation to perform
            
        Raises:
            ValueError: If an unknown operation type is provided
        """
        if operation == OperationType.VIEW:
            self.view_balance()
        elif operation == OperationType.CREDIT:
            self.credit_account_cli()
        elif operation == OperationType.DEBIT:
            self.debit_account_cli()
        else:
            raise ValueError(f"Unknown operation type: {operation}")
