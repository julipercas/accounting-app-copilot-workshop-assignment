"""Input validation functions for the accounting application.

This module centralizes all validation logic to follow DRY principles
and provide comprehensive security checks on user input.
"""

from decimal import Decimal, InvalidOperation

from constants import ZERO, MAX_AMOUNT
from exceptions import InvalidAmountError


def validate_amount(user_input: str) -> Decimal:
    """Validate and convert user input to a Decimal amount.
    
    Performs comprehensive validation to ensure the amount is:
    - Not empty
    - A valid numeric value
    - Non-negative
    - Within the maximum allowed value
    - Has at most 2 decimal places
    
    Args:
        user_input: The raw string input from the user
        
    Returns:
        A validated Decimal amount
        
    Raises:
        InvalidAmountError: If the input fails any validation check
        
    Examples:
        >>> validate_amount("100.50")
        Decimal('100.50')
        >>> validate_amount("  50  ")
        Decimal('50')
        >>> validate_amount("-10")
        Raises InvalidAmountError
    """
    # Strip whitespace
    user_input = user_input.strip()
    
    # Check for empty input
    if not user_input:
        raise InvalidAmountError("Amount cannot be empty")
    
    # Convert to Decimal and validate numeric format
    try:
        amount = Decimal(user_input)
    except InvalidOperation:
        raise InvalidAmountError(f"Invalid numeric value: '{user_input}'")
    
    # Check for negative amounts
    if amount < ZERO:
        raise InvalidAmountError(f"Amount cannot be negative: {amount}")
    
    # Check for excessive precision (more than 2 decimal places)
    if amount.as_tuple().exponent < -2:
        raise InvalidAmountError(
            f"Amount cannot have more than 2 decimal places: {amount}"
        )
    
    # Check maximum value
    if amount > MAX_AMOUNT:
        raise InvalidAmountError(
            f"Amount exceeds maximum allowed value of {MAX_AMOUNT}: {amount}"
        )
    
    return amount


def validate_menu_choice(user_input: str) -> int:
    """Validate and convert user input to a menu choice.
    
    Args:
        user_input: The raw string input from the user
        
    Returns:
        A validated integer menu choice (1-4)
        
    Raises:
        InvalidAmountError: If the input is not a valid menu choice
        
    Examples:
        >>> validate_menu_choice("1")
        1
        >>> validate_menu_choice("  3  ")
        3
        >>> validate_menu_choice("5")
        Raises InvalidAmountError
    """
    # Strip whitespace
    user_input = user_input.strip()
    
    # Check for empty input
    if not user_input:
        raise InvalidAmountError("Choice cannot be empty")
    
    # Convert to integer
    try:
        choice = int(user_input)
    except ValueError:
        raise InvalidAmountError(f"Invalid menu choice: '{user_input}'")
    
    # Validate range
    if choice < 1 or choice > 4:
        raise InvalidAmountError(f"Menu choice must be between 1 and 4: {choice}")
    
    return choice
