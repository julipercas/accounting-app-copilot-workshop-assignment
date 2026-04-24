"""Unit tests for the data layer.

This module tests the AccountData implementation for proper persistence
and error handling.
"""

import json
import pytest
from decimal import Decimal
from pathlib import Path

from data import AccountData
from constants import INITIAL_BALANCE
from exceptions import DataPersistenceError


class TestAccountData:
    """Test cases for AccountData class."""
    
    def test_initialization_creates_file(self, tmp_path):
        """Test that initialization creates data file with initial balance."""
        data_file = tmp_path / "test_balance.json"
        data = AccountData(data_file)
        
        assert data_file.exists()
        assert data.read_balance() == INITIAL_BALANCE
        
        # Verify file contents
        with data_file.open('r') as f:
            content = json.load(f)
        assert Decimal(content['balance']) == INITIAL_BALANCE
    
    def test_initialization_loads_existing_file(self, tmp_path):
        """Test that initialization loads balance from existing file."""
        data_file = tmp_path / "test_balance.json"
        expected_balance = Decimal("2500.75")
        
        # Create file with known balance
        with data_file.open('w') as f:
            json.dump({'balance': str(expected_balance)}, f)
        
        # Load and verify
        data = AccountData(data_file)
        assert data.read_balance() == expected_balance
    
    def test_write_balance_persists(self, tmp_path):
        """Test that write_balance saves to file."""
        data_file = tmp_path / "test_balance.json"
        data = AccountData(data_file)
        
        new_balance = Decimal("500.25")
        data.write_balance(new_balance)
        
        assert data.read_balance() == new_balance
        
        # Verify persistence
        with data_file.open('r') as f:
            content = json.load(f)
        assert Decimal(content['balance']) == new_balance
    
    def test_persistence_across_instances(self, tmp_path):
        """Test that balance persists across AccountData instances."""
        data_file = tmp_path / "test_balance.json"
        
        # Create and modify balance
        data1 = AccountData(data_file)
        data1.write_balance(Decimal("750.50"))
        
        # Create new instance and verify
        data2 = AccountData(data_file)
        assert data2.read_balance() == Decimal("750.50")
    
    def test_corrupted_file_recovery(self, tmp_path):
        """Test that corrupted file is handled gracefully."""
        data_file = tmp_path / "test_balance.json"
        
        # Create corrupted file
        with data_file.open('w') as f:
            f.write("not valid json {{{")
        
        # Should recover with initial balance
        data = AccountData(data_file)
        assert data.read_balance() == INITIAL_BALANCE
    
    def test_missing_balance_key_recovery(self, tmp_path):
        """Test that file with missing balance key is handled gracefully."""
        data_file = tmp_path / "test_balance.json"
        
        # Create file without balance key
        with data_file.open('w') as f:
            json.dump({'wrong_key': '1000'}, f)
        
        # Should recover with initial balance
        data = AccountData(data_file)
        assert data.read_balance() == INITIAL_BALANCE
    
    def test_negative_balance_recovery(self, tmp_path):
        """Test that negative balance in file is handled gracefully."""
        data_file = tmp_path / "test_balance.json"
        
        # Create file with negative balance
        with data_file.open('w') as f:
            json.dump({'balance': '-100.00'}, f)
        
        # Should recover with initial balance
        data = AccountData(data_file)
        assert data.read_balance() == INITIAL_BALANCE
    
    def test_write_balance_type_validation(self, tmp_path):
        """Test that write_balance validates Decimal type."""
        data_file = tmp_path / "test_balance.json"
        data = AccountData(data_file)
        
        # Should raise ValueError for non-Decimal types
        with pytest.raises(ValueError, match="must be a Decimal"):
            data.write_balance(100)  # int
        with pytest.raises(ValueError, match="must be a Decimal"):
            data.write_balance("100")  # string
        with pytest.raises(ValueError, match="must be a Decimal"):
            data.write_balance(100.50)  # float
    
    def test_directory_creation(self, tmp_path):
        """Test that parent directories are created if needed."""
        data_file = tmp_path / "subdir" / "nested" / "balance.json"
        data = AccountData(data_file)
        
        assert data_file.exists()
        assert data_file.parent.exists()
        assert data.read_balance() == INITIAL_BALANCE
