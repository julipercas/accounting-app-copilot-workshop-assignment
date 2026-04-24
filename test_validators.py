"""Unit tests for the validators module.

This module tests all validation functions to ensure they properly
validate and reject invalid inputs.
"""

import pytest
from decimal import Decimal

from validators import validate_amount, validate_menu_choice
from exceptions import InvalidAmountError
from constants import ZERO, MAX_AMOUNT


class TestValidateAmount:
    """Test cases for validate_amount function."""
    
    def test_valid_amount(self):
        """Test validation of valid numeric amounts."""
        assert validate_amount("100.50") == Decimal("100.50")
        assert validate_amount("0.01") == Decimal("0.01")
        assert validate_amount("999999.99") == Decimal("999999.99")
    
    def test_valid_amount_with_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        assert validate_amount("  50.00  ") == Decimal("50.00")
        assert validate_amount("\t100\t") == Decimal("100")
    
    def test_zero_amount(self):
        """Test that zero is valid format-wise (business logic rejects it)."""
        assert validate_amount("0") == ZERO
        assert validate_amount("0.00") == ZERO
    
    def test_amount_without_decimals(self):
        """Test that amounts without decimal points are valid."""
        assert validate_amount("100") == Decimal("100")
        assert validate_amount("50") == Decimal("50")
    
    def test_empty_input(self):
        """Test that empty input raises InvalidAmountError."""
        with pytest.raises(InvalidAmountError, match="cannot be empty"):
            validate_amount("")
        with pytest.raises(InvalidAmountError, match="cannot be empty"):
            validate_amount("   ")
    
    def test_negative_amount(self):
        """Test that negative amounts are rejected."""
        with pytest.raises(InvalidAmountError, match="cannot be negative"):
            validate_amount("-10.00")
        with pytest.raises(InvalidAmountError, match="cannot be negative"):
            validate_amount("-0.01")
    
    def test_non_numeric_input(self):
        """Test that non-numeric input is rejected."""
        with pytest.raises(InvalidAmountError, match="Invalid numeric value"):
            validate_amount("abc")
        with pytest.raises(InvalidAmountError, match="Invalid numeric value"):
            validate_amount("12.34.56")
        with pytest.raises(InvalidAmountError, match="Invalid numeric value"):
            validate_amount("$100")
    
    def test_excessive_precision(self):
        """Test that amounts with more than 2 decimal places are rejected."""
        with pytest.raises(InvalidAmountError, match="more than 2 decimal places"):
            validate_amount("10.123")
        with pytest.raises(InvalidAmountError, match="more than 2 decimal places"):
            validate_amount("5.999")
    
    def test_maximum_amount(self):
        """Test that the maximum amount is accepted and exceeded amounts rejected."""
        assert validate_amount("999999.99") == MAX_AMOUNT
        with pytest.raises(InvalidAmountError, match="exceeds maximum"):
            validate_amount("1000000.00")
        with pytest.raises(InvalidAmountError, match="exceeds maximum"):
            validate_amount("9999999.99")


class TestValidateMenuChoice:
    """Test cases for validate_menu_choice function."""
    
    def test_valid_choices(self):
        """Test validation of valid menu choices (1-4)."""
        assert validate_menu_choice("1") == 1
        assert validate_menu_choice("2") == 2
        assert validate_menu_choice("3") == 3
        assert validate_menu_choice("4") == 4
    
    def test_valid_choice_with_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        assert validate_menu_choice("  1  ") == 1
        assert validate_menu_choice("\t3\t") == 3
    
    def test_empty_input(self):
        """Test that empty input raises InvalidAmountError."""
        with pytest.raises(InvalidAmountError, match="cannot be empty"):
            validate_menu_choice("")
        with pytest.raises(InvalidAmountError, match="cannot be empty"):
            validate_menu_choice("   ")
    
    def test_non_integer_input(self):
        """Test that non-integer input is rejected."""
        with pytest.raises(InvalidAmountError, match="Invalid menu choice"):
            validate_menu_choice("abc")
        with pytest.raises(InvalidAmountError, match="Invalid menu choice"):
            validate_menu_choice("1.5")
        with pytest.raises(InvalidAmountError, match="Invalid menu choice"):
            validate_menu_choice("two")
    
    def test_out_of_range_choices(self):
        """Test that choices outside 1-4 range are rejected."""
        with pytest.raises(InvalidAmountError, match="must be between 1 and 4"):
            validate_menu_choice("0")
        with pytest.raises(InvalidAmountError, match="must be between 1 and 4"):
            validate_menu_choice("5")
        with pytest.raises(InvalidAmountError, match="must be between 1 and 4"):
            validate_menu_choice("-1")
        with pytest.raises(InvalidAmountError, match="must be between 1 and 4"):
            validate_menu_choice("100")
