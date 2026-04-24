"""Integration tests for the complete accounting system.

This module tests the full application stack with real components
to ensure all layers work together correctly.
"""

import pytest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from data import AccountData
from operations import AccountOperations
from ui import AccountUI
from constants import INITIAL_BALANCE


class TestIntegration:
    """Integration tests for the complete system."""
    
    @pytest.fixture
    def app_stack(self, tmp_path):
        """Create full application stack with isolated data file."""
        data_file = tmp_path / "test_balance.json"
        data_store = AccountData(data_file)
        operations = AccountOperations(data_store)
        ui = AccountUI(operations)
        return ui, operations, data_store
    
    def test_tc_1_1_view_initial_balance(self, app_stack, capsys):
        """Test TC-1.1: View initial balance of 1000.00."""
        ui, operations, data_store = app_stack
        
        operations.view_balance()
        
        captured = capsys.readouterr()
        assert "Current balance: $1000.00" in captured.out
    
    @patch('builtins.input', return_value="100.00")
    def test_tc_2_1_credit_valid_amount(self, mock_input, app_stack, capsys):
        """Test TC-2.1: Credit 100.00, verify balance becomes 1100.00."""
        ui, operations, data_store = app_stack
        
        operations.credit_account_cli()
        
        assert data_store.read_balance() == Decimal("1100.00")
        captured = capsys.readouterr()
        assert "Credit successful" in captured.out
    
    @patch('builtins.input', return_value="0.00")
    def test_tc_2_2_credit_zero_amount(self, mock_input, app_stack, capsys):
        """Test TC-2.2: Credit 0.00, balance should remain 1000.00."""
        ui, operations, data_store = app_stack
        
        operations.credit_account_cli()
        
        assert data_store.read_balance() == INITIAL_BALANCE
        captured = capsys.readouterr()
        assert "Amount must be greater than zero" in captured.out
    
    @patch('builtins.input', return_value="50.00")
    def test_tc_3_1_debit_valid_amount(self, mock_input, app_stack, capsys):
        """Test TC-3.1: Debit 50.00, verify balance becomes 950.00."""
        ui, operations, data_store = app_stack
        
        operations.debit_account_cli()
        
        assert data_store.read_balance() == Decimal("950.00")
        captured = capsys.readouterr()
        assert "Debit successful" in captured.out
    
    @patch('builtins.input', return_value="1500.00")
    def test_tc_3_2_debit_insufficient_funds(self, mock_input, app_stack, capsys):
        """Test TC-3.2: Debit 1500.00 with 1000.00 balance, should fail."""
        ui, operations, data_store = app_stack
        
        operations.debit_account_cli()
        
        # Balance should remain unchanged
        assert data_store.read_balance() == INITIAL_BALANCE
        captured = capsys.readouterr()
        assert "Insufficient funds" in captured.out
    
    @patch('builtins.input', return_value="0.00")
    def test_tc_3_3_debit_zero_amount(self, mock_input, app_stack, capsys):
        """Test TC-3.3: Debit 0.00, balance should remain 1000.00."""
        ui, operations, data_store = app_stack
        
        operations.debit_account_cli()
        
        assert data_store.read_balance() == INITIAL_BALANCE
        captured = capsys.readouterr()
        assert "Amount must be greater than zero" in captured.out
    
    @patch('builtins.input', side_effect=["4"])
    def test_tc_4_1_exit_application(self, mock_input, app_stack, capsys):
        """Test TC-4.1: Exit application cleanly."""
        ui, operations, data_store = app_stack
        
        ui.run()
        
        captured = capsys.readouterr()
        assert "Thank you for using" in captured.out or "Goodbye" in captured.out
    
    @patch('builtins.input', side_effect=["100.00", "50.00"])
    def test_full_workflow_credit_then_debit(self, mock_input, app_stack, capsys):
        """Test complete workflow: credit then debit."""
        ui, operations, data_store = app_stack
        
        # Initial balance
        assert data_store.read_balance() == Decimal("1000.00")
        
        # Credit 100
        operations.credit_account_cli()
        assert data_store.read_balance() == Decimal("1100.00")
        
        # Debit 50
        operations.debit_account_cli()
        assert data_store.read_balance() == Decimal("1050.00")
    
    def test_persistence_across_restarts(self, tmp_path):
        """Test that balance persists across application restarts."""
        data_file = tmp_path / "persistent_balance.json"
        
        # First session: credit 200
        data1 = AccountData(data_file)
        ops1 = AccountOperations(data1)
        success, message = ops1.credit_account(Decimal("200.00"))
        assert success
        assert data1.read_balance() == Decimal("1200.00")
        
        # Second session: verify balance persisted, then debit 100
        data2 = AccountData(data_file)
        ops2 = AccountOperations(data2)
        assert data2.read_balance() == Decimal("1200.00")
        success, message = ops2.debit_account(Decimal("100.00"))
        assert success
        assert data2.read_balance() == Decimal("1100.00")
        
        # Third session: verify final balance
        data3 = AccountData(data_file)
        assert data3.read_balance() == Decimal("1100.00")
    
    @patch('builtins.input', side_effect=["invalid", "1", "4"])
    def test_ui_handles_invalid_menu_choice(self, mock_input, app_stack, capsys):
        """Test that UI handles invalid menu choices gracefully."""
        ui, operations, data_store = app_stack
        
        ui.run()
        
        captured = capsys.readouterr()
        assert "Invalid choice" in captured.out
    
    @patch('builtins.input', side_effect=["2", "invalid_amount", "4"])
    def test_operations_handle_invalid_amount(self, mock_input, app_stack, capsys):
        """Test that operations handle invalid amounts gracefully."""
        ui, operations, data_store = app_stack
        
        ui.run()
        
        # Balance should remain unchanged
        assert data_store.read_balance() == INITIAL_BALANCE
        captured = capsys.readouterr()
        assert "Invalid amount" in captured.out
