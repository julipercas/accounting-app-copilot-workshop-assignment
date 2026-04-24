"""Unit tests for the Flask web application.

This module tests all Flask routes and web functionality to ensure
proper operation of the browser-based interface.
"""

import pytest
from decimal import Decimal
from pathlib import Path

from app import app as flask_app
from data import AccountData
from operations import AccountOperations


@pytest.fixture
def app(tmp_path):
    """Create Flask test app with isolated data file."""
    # Configure test data file
    test_data_file = tmp_path / "test_balance.json"
    
    # Create fresh instances for testing
    data_store = AccountData(test_data_file)
    ops = AccountOperations(data_store)
    
    # Update Flask app to use test instances
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    
    # Replace global instances with test instances
    import app as app_module
    app_module.data_store = data_store
    app_module.operations = ops
    
    yield flask_app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


class TestRoutes:
    """Test Flask route responses."""
    
    def test_index_page(self, client):
        """Test home page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Account Overview' in response.data
        assert b'Current Balance' in response.data
    
    def test_credit_page_get(self, client):
        """Test credit page loads successfully."""
        response = client.get('/credit')
        assert response.status_code == 200
        assert b'Credit Account' in response.data
        assert b'Amount to Credit' in response.data
    
    def test_debit_page_get(self, client):
        """Test debit page loads successfully."""
        response = client.get('/debit')
        assert response.status_code == 200
        assert b'Debit Account' in response.data
        assert b'Amount to Debit' in response.data
    
    def test_history_page(self, client):
        """Test history page loads successfully."""
        response = client.get('/history')
        assert response.status_code == 200
        assert b'Transaction History' in response.data
    
    def test_stats_page(self, client):
        """Test statistics page loads successfully."""
        response = client.get('/stats')
        assert response.status_code == 200
        assert b'Account Statistics' in response.data


class TestCreditOperations:
    """Test credit operations through web interface."""
    
    def test_credit_valid_amount(self, client):
        """Test crediting a valid amount."""
        response = client.post('/credit', data={'amount': '100.00'}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Credit successful' in response.data
        assert b'$1,100.00' in response.data
    
    def test_credit_zero_amount(self, client):
        """Test that zero amount is rejected."""
        response = client.post('/credit', data={'amount': '0.00'}, follow_redirects=True)
        assert response.status_code == 200
        assert b'greater than zero' in response.data
    
    def test_credit_negative_amount(self, client):
        """Test that negative amount is rejected."""
        response = client.post('/credit', data={'amount': '-50.00'}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid amount' in response.data or b'cannot be negative' in response.data
    
    def test_credit_invalid_input(self, client):
        """Test that invalid input is rejected."""
        response = client.post('/credit', data={'amount': 'invalid'}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid amount' in response.data or b'Invalid numeric value' in response.data
    
    def test_credit_excessive_precision(self, client):
        """Test that excessive decimal precision is rejected."""
        response = client.post('/credit', data={'amount': '10.123'}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid amount' in response.data or b'decimal places' in response.data


class TestDebitOperations:
    """Test debit operations through web interface."""
    
    def test_debit_valid_amount(self, client):
        """Test debiting a valid amount."""
        response = client.post('/debit', data={'amount': '50.00'}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Debit successful' in response.data
        assert b'$950.00' in response.data
    
    def test_debit_insufficient_funds(self, client):
        """Test that debit fails with insufficient funds."""
        response = client.post('/debit', data={'amount': '1500.00'}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Insufficient funds' in response.data
        assert b'$1,000.00' in response.data  # Balance unchanged
    
    def test_debit_zero_amount(self, client):
        """Test that zero amount is rejected."""
        response = client.post('/debit', data={'amount': '0.00'}, follow_redirects=True)
        assert response.status_code == 200
        assert b'greater than zero' in response.data
    
    def test_debit_negative_amount(self, client):
        """Test that negative amount is rejected."""
        response = client.post('/debit', data={'amount': '-25.00'}, follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid amount' in response.data or b'cannot be negative' in response.data


class TestTransactionHistory:
    """Test transaction history functionality."""
    
    def test_empty_history(self, client):
        """Test history page with no transactions."""
        response = client.get('/history')
        assert response.status_code == 200
        assert b'No transaction history' in response.data or b'No transactions yet' in response.data
    
    def test_history_after_transactions(self, client):
        """Test that transactions appear in history."""
        # Perform a credit
        client.post('/credit', data={'amount': '100.00'})
        
        # Check history
        response = client.get('/history')
        assert response.status_code == 200
        assert b'Credit' in response.data
        assert b'$100.00' in response.data
    
    def test_history_shows_multiple_transactions(self, client):
        """Test that multiple transactions are recorded."""
        # Perform multiple transactions
        client.post('/credit', data={'amount': '200.00'})
        client.post('/debit', data={'amount': '50.00'})
        
        # Check history
        response = client.get('/history')
        assert response.status_code == 200
        assert b'Credit' in response.data
        assert b'Debit' in response.data
        assert response.data.count(b'<tr class="txn-') >= 2


class TestStatistics:
    """Test statistics page functionality."""
    
    def test_stats_initial_state(self, client):
        """Test statistics with no transactions."""
        response = client.get('/stats')
        assert response.status_code == 200
        assert b'Total Credits' in response.data
        assert b'Total Debits' in response.data
    
    def test_stats_after_transactions(self, client):
        """Test that statistics update after transactions."""
        # Perform transactions
        client.post('/credit', data={'amount': '300.00'})
        client.post('/debit', data={'amount': '100.00'})
        
        # Check stats
        response = client.get('/stats')
        assert response.status_code == 200
        assert b'$300.00' in response.data  # Total credits
        assert b'$100.00' in response.data  # Total debits


class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_full_workflow(self, client):
        """Test complete workflow: view, credit, debit, history."""
        # View initial balance
        response = client.get('/')
        assert b'$1,000.00' in response.data
        
        # Credit account
        response = client.post('/credit', data={'amount': '500.00'}, follow_redirects=True)
        assert b'$1,500.00' in response.data
        
        # Debit account
        response = client.post('/debit', data={'amount': '200.00'}, follow_redirects=True)
        assert b'$1,300.00' in response.data
        
        # Check history
        response = client.get('/history')
        assert b'Credit' in response.data
        assert b'Debit' in response.data
        assert b'$500.00' in response.data
        assert b'$200.00' in response.data
    
    def test_persistence_across_requests(self, client):
        """Test that balance persists across multiple requests."""
        # Credit account
        client.post('/credit', data={'amount': '250.00'})
        
        # Verify on home page
        response = client.get('/')
        assert b'$1,250.00' in response.data
        
        # Verify on credit page
        response = client.get('/credit')
        assert b'$1,250.00' in response.data
        
        # Verify on debit page
        response = client.get('/debit')
        assert b'$1,250.00' in response.data
