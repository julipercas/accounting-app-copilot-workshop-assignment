"""Flask web application for the accounting system.

This module provides a browser-based interface to the accounting system,
implementing the same operations as the CLI version with added features
like transaction history and statistics visualization.
"""

import json
import logging
from datetime import datetime
from decimal import Decimal

from flask import Flask, render_template, request, redirect, url_for, flash

from data import AccountData
from operations import AccountOperations
from validators import validate_amount
from exceptions import InvalidAmountError


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'accounting-system-secret-key-change-in-production'

# Create singleton instances
data_store = AccountData()
operations = AccountOperations(data_store)


# Template filters
@app.template_filter('format_currency')
def format_currency(value: Decimal) -> str:
    """Format a Decimal as currency with $ symbol.
    
    Args:
        value: Decimal value to format
        
    Returns:
        Formatted string like "$1,234.56"
    """
    return f"${value:,.2f}"


@app.template_filter('format_datetime')
def format_datetime(value: str) -> str:
    """Format ISO datetime string for display.
    
    Args:
        value: ISO format datetime string
        
    Returns:
        Formatted string like "Jan 15, 2026 2:30 PM"
    """
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%b %d, %Y %I:%M %P")
    except (ValueError, AttributeError):
        return value


@app.template_filter('transaction_type_label')
def transaction_type_label(value: str) -> str:
    """Format transaction type for display.
    
    Args:
        value: Transaction type ('credit' or 'debit')
        
    Returns:
        Capitalized type name
    """
    return value.capitalize()


# Routes
@app.route('/')
def index():
    """Home page showing current balance and recent transactions."""
    try:
        balance = data_store.read_balance()
        recent_transactions = data_store.get_transactions(limit=5)
        
        return render_template(
            'index.html',
            balance=balance,
            transactions=recent_transactions
        )
    except Exception as e:
        logger.error(f"Error loading home page: {e}", exc_info=True)
        flash("An error occurred loading the page", "error")
        return render_template('index.html', balance=Decimal('0'), transactions=[])


@app.route('/credit', methods=['GET', 'POST'])
def credit():
    """Credit account page with form."""
    if request.method == 'POST':
        try:
            # Get and validate amount
            amount_str = request.form.get('amount', '').strip()
            amount = validate_amount(amount_str)
            
            # Process credit
            success, message = operations.credit_account(amount)
            
            if success:
                flash(message, "success")
            else:
                flash(message, "error")
                
        except InvalidAmountError as e:
            flash(f"Invalid amount: {e}", "error")
        except Exception as e:
            logger.error(f"Credit error: {e}", exc_info=True)
            flash("An unexpected error occurred", "error")
        
        # Stay on credit page after POST with feedback
        return redirect(url_for('credit'))
    
    # GET request - show form
    balance = data_store.read_balance()
    return render_template('credit.html', balance=balance)


@app.route('/debit', methods=['GET', 'POST'])
def debit():
    """Debit account page with form."""
    if request.method == 'POST':
        try:
            # Get and validate amount
            amount_str = request.form.get('amount', '').strip()
            amount = validate_amount(amount_str)
            
            # Process debit
            success, message = operations.debit_account(amount)
            
            if success:
                flash(message, "success")
            else:
                flash(message, "error")
                
        except InvalidAmountError as e:
            flash(f"Invalid amount: {e}", "error")
        except Exception as e:
            logger.error(f"Debit error: {e}", exc_info=True)
            flash("An unexpected error occurred", "error")
        
        # Stay on debit page after POST with feedback
        return redirect(url_for('debit'))
    
    # GET request - show form
    balance = data_store.read_balance()
    return render_template('debit.html', balance=balance)


@app.route('/history')
def history():
    """Transaction history page."""
    try:
        transactions = data_store.get_transactions()
        return render_template('history.html', transactions=transactions)
    except Exception as e:
        logger.error(f"Error loading history: {e}", exc_info=True)
        flash("An error occurred loading transaction history", "error")
        return render_template('history.html', transactions=[])


@app.route('/stats')
def stats():
    """Statistics and visualization page."""
    try:
        stats_data = data_store.get_transaction_stats()
        transactions = data_store.get_transactions()
        balance = data_store.read_balance()
        
        # Prepare transaction data for JavaScript charts
        transactions_json = json.dumps([
            {
                'timestamp': txn.timestamp,
                'type': txn.type,
                'amount': float(txn.amount),
                'balance': float(txn.balance_after)
            }
            for txn in transactions
        ])
        
        return render_template(
            'stats.html',
            stats=stats_data,
            balance=balance,
            transactions_json=transactions_json
        )
    except Exception as e:
        logger.error(f"Error loading stats: {e}", exc_info=True)
        flash("An error occurred loading statistics", "error")
        return render_template('stats.html', stats={}, balance=Decimal('0'), transactions_json='[]')


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return render_template('error.html', error_code=404, error_message="Page not found"), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}", exc_info=True)
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500


if __name__ == '__main__':
    logger.info("Starting Flask web application")
    app.run(debug=True, host='localhost', port=5000)
