"""Constants and configuration for the accounting application.

This module centralizes all configuration values, enums, and constants
used throughout the application to follow DRY principles.
"""

from decimal import Decimal, getcontext, ROUND_HALF_UP
from enum import Enum
from pathlib import Path


# Configure decimal precision for financial calculations
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_UP


class OperationType(Enum):
    """Enumeration of supported account operations.
    
    Replaces COBOL's fixed-width string constants ('TOTAL ', 'CREDIT', 'DEBIT ')
    with type-safe enum values.
    """
    VIEW = "view"
    CREDIT = "credit"
    DEBIT = "debit"


# Financial constants
INITIAL_BALANCE = Decimal('1000.00')
ZERO = Decimal('0.00')
MAX_AMOUNT = Decimal('999999.99')  # Maximum from COBOL PIC 9(6)V99

# File paths
DATA_FILE = Path('balance.json')

# Menu configuration
MENU_OPTIONS = {
    1: ("View Balance", OperationType.VIEW),
    2: ("Credit Account", OperationType.CREDIT),
    3: ("Debit Account", OperationType.DEBIT),
    4: ("Exit", None)
}

MENU_TEXT = """
=====================================
    ACCOUNTING SYSTEM MENU
=====================================
1. View Balance
2. Credit Account
3. Debit Account
4. Exit
=====================================
"""
