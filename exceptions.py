"""Custom exceptions for the accounting application.

This module defines a hierarchy of exceptions that provide clear error
semantics and enable specific error handling throughout the application.
"""


class AccountingError(Exception):
    """Base exception for all accounting application errors.
    
    All custom exceptions in this application inherit from this base class,
    making it easy to catch any application-specific error.
    """
    pass


class InsufficientFundsError(AccountingError):
    """Raised when attempting to debit more than the available balance.
    
    This exception is raised during debit operations when the requested
    amount exceeds the current account balance.
    """
    pass


class InvalidAmountError(AccountingError):
    """Raised when an invalid amount is provided.
    
    This exception is raised when:
    - The amount is negative
    - The amount is not a valid numeric value
    - The amount exceeds the maximum allowed value
    - The amount has more than 2 decimal places
    - The input is empty or contains invalid characters
    """
    pass


class DataPersistenceError(AccountingError):
    """Raised when data cannot be saved or loaded from persistent storage.
    
    This exception is raised when file I/O operations fail, such as:
    - Unable to read the data file
    - Unable to write to the data file
    - File contains corrupted data
    - Permission denied errors
    """
    pass
