"""Unit tests for the operations layer.

This module tests the business logic for account operations using mocked
data layer to isolate the business logic from persistence.
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, call

from operations import AccountOperations
from constants import OperationType, ZERO, INITIAL_BALANCE
from exceptions import InsufficientFundsError, InvalidAmountError


class TestAccountOperations:
    """Test cases for AccountOperations class."""
    
    @pytest.fixture
    def mock_data_store(self):
        """Create a mock data store for testing."""
        mock = Mock()
        mock.read_balance.return_value = INITIAL_BALANCE
        return mock
    
    @pytest.fixture
    def operations(self, mock_data_store):
        """Create AccountOperations instance with mock data store."""
        return AccountOperations(mock_data_store)
    
    def test_view_balance(self, operations, mock_data_store, capsys):
        """Test TC-1.1: View current balance."""
        mock_data_store.read_balance.return_value = Decimal("1000.00")
        
        operations.view_balance()
        
        captured = capsys.readouterr()
        assert "Current balance: $1000.00" in captured.out
        mock_data_store.read_balance.assert_called_once()
    
    @patch('builtins.input', return_value="100.00")
    def test_credit_valid_amount(self, mock_input, operations, mock_data_store, capsys):
        """Test TC-2.1: Credit account with valid amount."""
        mock_data_store.read_balance.return_value = Decimal("1000.00")
        
        operations.credit_account_cli()
        
        # Verify balance was updated
        mock_data_store.write_balance.assert_called_with(Decimal("1100.00"), 'credit', Decimal("100.00"))
        
        captured = capsys.readouterr()
        assert "Credit successful: $100.00" in captured.out
        assert "New balance: $1100.00" in captured.out
    
    @patch('builtins.input', return_value="0.00")
    def test_credit_zero_amount(self, mock_input, operations, mock_data_store, capsys):
        """Test TC-2.2: Credit with zero amount (should be rejected)."""
        operations.credit_account_cli()
        
        # Verify balance was NOT updated
        mock_data_store.write_balance.assert_not_called()
        
        captured = capsys.readouterr()
        assert "Amount must be greater than zero" in captured.out
    
    @patch('builtins.input', return_value="50.00")
    def test_debit_valid_amount(self, mock_input, operations, mock_data_store, capsys):
        """Test TC-3.1: Debit account with valid amount within balance."""
        mock_data_store.read_balance.return_value = Decimal("1000.00")
        
        operations.debit_account_cli()
        
        # Verify balance was updated
        mock_data_store.write_balance.assert_called_with(Decimal("950.00"), 'debit', Decimal("50.00"))
        
        captured = capsys.readouterr()
        assert "Debit successful: $50.00" in captured.out
        assert "New balance: $950.00" in captured.out
    
    @patch('builtins.input', return_value="1500.00")
    def test_debit_insufficient_funds(self, mock_input, operations, mock_data_store, capsys):
        """Test TC-3.2: Debit exceeding balance (should fail)."""
        mock_data_store.read_balance.return_value = Decimal("1000.00")
        
        operations.debit_account_cli()
        
        # Verify balance was NOT updated
        mock_data_store.write_balance.assert_not_called()
        
        captured = capsys.readouterr()
        assert "Insufficient funds" in captured.out
    
    @patch('builtins.input', return_value="0.00")
    def test_debit_zero_amount(self, mock_input, operations, mock_data_store, capsys):
        """Test TC-3.3: Debit with zero amount (should be rejected)."""
        operations.debit_account_cli()
        
        # Verify balance was NOT updated
        mock_data_store.write_balance.assert_not_called()
        
        captured = capsys.readouterr()
        assert "Amount must be greater than zero" in captured.out
    
    @patch('builtins.input', return_value="invalid")
    def test_credit_invalid_input(self, mock_input, operations, mock_data_store, capsys):
        """Test credit with invalid non-numeric input."""
        operations.credit_account_cli()
        
        # Verify balance was NOT updated
        mock_data_store.write_balance.assert_not_called()
        
        captured = capsys.readouterr()
        assert "Invalid amount" in captured.out
    
    @patch('builtins.input', return_value="-50.00")
    def test_credit_negative_amount(self, mock_input, operations, mock_data_store, capsys):
        """Test credit with negative amount (should be rejected)."""
        operations.credit_account_cli()
        
        # Verify balance was NOT updated
        mock_data_store.write_balance.assert_not_called()
        
        captured = capsys.readouterr()
        assert "Invalid amount" in captured.out
    
    @patch('builtins.input', return_value="1000000.00")
    def test_credit_excessive_amount(self, mock_input, operations, mock_data_store, capsys):
        """Test credit with amount exceeding maximum."""
        operations.credit_account_cli()
        
        # Verify balance was NOT updated
        mock_data_store.write_balance.assert_not_called()
        
        captured = capsys.readouterr()
        assert "Invalid amount" in captured.out
    
    def test_handle_operation_view(self, operations, mock_data_store, capsys):
        """Test handle_operation routes VIEW correctly."""
        mock_data_store.read_balance.return_value = Decimal("1000.00")
        
        operations.handle_operation(OperationType.VIEW)
        
        captured = capsys.readouterr()
        assert "Current balance" in captured.out
    
    @patch('builtins.input', return_value="100.00")
    def test_handle_operation_credit(self, mock_input, operations, mock_data_store, capsys):
        """Test handle_operation routes CREDIT correctly."""
        mock_data_store.read_balance.return_value = Decimal("1000.00")
        
        operations.handle_operation(OperationType.CREDIT)
        
        mock_data_store.write_balance.assert_called_with(Decimal("1100.00"), 'credit', Decimal("100.00"))
    
    @patch('builtins.input', return_value="50.00")
    def test_handle_operation_debit(self, mock_input, operations, mock_data_store, capsys):
        """Test handle_operation routes DEBIT correctly."""
        mock_data_store.read_balance.return_value = Decimal("1000.00")
        
        operations.handle_operation(OperationType.DEBIT)
        
        mock_data_store.write_balance.assert_called_with(Decimal("950.00"), 'debit', Decimal("50.00"))
    
    def test_handle_operation_unknown(self, operations, mock_data_store):
        """Test handle_operation rejects unknown operation type."""
        with pytest.raises(ValueError, match="Unknown operation type"):
            operations.handle_operation("INVALID")
