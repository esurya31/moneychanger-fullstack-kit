"""
Transaction Processing Module for Money Changer Application
Handles buy/sell transactions, inventory updates, and receipt generation
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import io

# Import database models and utilities
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import (
    transaction_model, currency_model, customer_model, inventory_model, user_model
)
from utils.auth import SessionManager, RoleManager, require_permission
from utils.helpers import (
    format_currency, format_number, show_success_message, show_error_message,
    show_info_message, create_data_table, validate_positive_number,
    show_denomination_input, get_currency_denominations, log_user_action,
    show_loading_spinner
)

class TransactionManager:
    """Transaction management class"""

    def __init__(self):
        self.transaction_model = transaction_model
        self.currency_model = currency_model
        self.customer_model = customer_model
        self.inventory_model = inventory_model

    def get_all_currencies(self) -> List[Dict]:
        """Get all active currencies"""
        return self.currency_model.get_all_currencies()

    def get_all_customers(self) -> List[Dict]:
        """Get all active customers"""
        return self.customer_model.get_all_customers()

    def search_customers(self, query: str) -> List[Dict]:
        """Search customers"""
        return self.customer_model.search_customers(query)

    def get_currency_by_code(self, code: str) -> Optional[Dict]:
        """Get currency by code"""
        return self.currency_model.get_currency_by_code(code)

    def calculate_idr_amount(self, foreign_amount: float, rate: float, transaction_type: str) -> float:
        """Calculate IDR amount based on transaction type"""
        if transaction_type == 'BUY':
            # We buy foreign currency from customer (pay IDR to customer)
            return foreign_amount * rate
        else:  # SELL
            # We sell foreign currency to customer (receive IDR from customer)
            return foreign_amount * rate

    def validate_inventory(self, currency_code: str, denominations: Dict[float, int],
                         transaction_type: str) -> bool:
        """Validate inventory for transaction"""
        if transaction_type == 'SELL':
            # Check if we have enough inventory for selling
            for denomination, quantity in denominations.items():
                if quantity > 0:
                    inventory = self.inventory_model.get_inventory_by_currency(currency_code)
                    current_qty = 0

                    for item in inventory:
                        if abs(item['denomination'] - denomination) < 0.01:
                            current_qty = item['quantity']
                            break

                    if current_qty < quantity:
                        show_error_message(
                            f"Insufficient inventory for {currency_code} {denomination}. "
                            f"Available: {current_qty}, Required: {quantity}"
                        )
                        return False
        return True

    def process_transaction(self, transaction_data: Dict) -> Optional[int]:
        """Process complete transaction with inventory updates"""
        try:
            user = SessionManager.get_current_user()
            if not user:
                show_error_message("User not authenticated")
                return None

            conn = self.transaction_model.db.get_connection()
            cursor = conn.cursor()

            try:
                # Start transaction
                cursor.execute("BEGIN TRANSACTION")

                # Generate transaction number
                transaction_number = self.transaction_model.generate_transaction_number()

                # Create transaction record
                cursor.execute('''
                    INSERT INTO transactions (
                        transaction_number, transaction_type, customer_id, user_id,
                        currency_code, foreign_amount, rate, idr_amount,
                        total_notes, notes, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'COMPLETED')
                ''', (
                    transaction_number,
                    transaction_data['transaction_type'],
                    transaction_data['customer_id'],
                    user['id'],
                    transaction_data['currency_code'],
                    transaction_data['foreign_amount'],
                    transaction_data['rate'],
                    transaction_data['idr_amount'],
                    transaction_data.get('total_notes'),
                    transaction_data.get('notes')
                ))

                transaction_id = cursor.lastrowid

                # Update inventory based on transaction type
                for denomination, quantity in transaction_data['denominations'].items():
                    if quantity > 0:
                        if transaction_data['transaction_type'] == 'BUY':
                            # We buy foreign currency (increase inventory)
                            quantity_change = quantity
                        else:  # SELL
                            # We sell foreign currency (decrease inventory)
                            quantity_change = -quantity

                        # Update inventory
                        cursor.execute('''
                            INSERT OR REPLACE INTO denomination_inventory
                            (currency_code, denomination, quantity, last_updated)
                            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                        ''', (
                            transaction_data['currency_code'],
                            denomination,
                            (SELECT COALESCE(quantity, 0) + ? FROM denomination_inventory
                             WHERE currency_code = ? AND denomination = ?),
                            quantity_change,
                            transaction_data['currency_code'],
                            denomination
                        ))

                        # More explicit update approach
                        cursor.execute('''
                            UPDATE denomination_inventory
                            SET quantity = quantity + ?,
                                last_updated = CURRENT_TIMESTAMP
                            WHERE currency_code = ? AND denomination = ?
                        ''', (quantity_change, transaction_data['currency_code'], denomination))

                # Record transaction denominations
                for denomination, quantity in transaction_data['denominations'].items():
                    if quantity > 0:
                        cursor.execute('''
                            INSERT INTO transaction_denominations
                            (transaction_id, currency_code, denomination, quantity)
                            VALUES (?, ?, ?, ?)
                        ''', (transaction_id, transaction_data['currency_code'], denomination, quantity))

                # Commit transaction
                conn.commit()

                # Log audit
                log_user_action("PROCESS_TRANSACTION", {
                    'table_name': 'transactions',
                    'record_id': transaction_id,
                    'new_values': {
                        'transaction_number': transaction_number,
                        'transaction_type': transaction_data['transaction_type'],
                        'foreign_amount': transaction_data['foreign_amount'],
                        'idr_amount': transaction_data['idr_amount']
                    }
                })

                show_success_message(f"Transaction {transaction_number} completed successfully!")
                return transaction_id

            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

        except Exception as e:
            show_error_message(f"Failed to process transaction: {str(e)}")
            return None

    def get_transaction_history(self, start_date: date, end_date: date,
                              customer_id: Optional[int] = None,
                              currency_code: Optional[str] = None) -> List[Dict]:
        """Get transaction history with filters"""
        conn = self.transaction_model.db.get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT t.*, c.full_name as customer_name, c.customer_code,
                   u.full_name as user_name, cur.name as currency_name, cur.symbol
            FROM transactions t
            JOIN customers c ON t.customer_id = c.id
            JOIN users u ON t.user_id = u.id
            JOIN currencies cur ON t.currency_code = cur.code
            WHERE DATE(t.transaction_date) BETWEEN ? AND ? AND t.status = 'COMPLETED'
        '''
        params = [start_date, end_date]

        if customer_id:
            query += ' AND t.customer_id = ?'
            params.append(customer_id)

        if currency_code:
            query += ' AND t.currency_code = ?'
            params.append(currency_code)

        query += ' ORDER BY t.transaction_date DESC'

        cursor.execute(query, params)
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return transactions

    def get_transaction_details(self, transaction_id: int) -> Optional[Dict]:
        """Get detailed transaction information including denominations"""
        conn = self.transaction_model.db.get_connection()
        cursor = conn.cursor()

        # Get transaction details
        cursor.execute('''
            SELECT t.*, c.full_name as customer_name, c.customer_code,
                   c.identity_number, c.country, c.phone,
                   u.full_name as user_name, cur.name as currency_name, cur.symbol
            FROM transactions t
            JOIN customers c ON t.customer_id = c.id
            JOIN users u ON t.user_id = u.id
            JOIN currencies cur ON t.currency_code = cur.code
            WHERE t.id = ?
        ''', (transaction_id,))

        transaction = cursor.fetchone()

        if transaction:
            transaction = dict(transaction)

            # Get transaction denominations
            cursor.execute('''
                SELECT denomination, quantity
                FROM transaction_denominations
                WHERE transaction_id = ?
                ORDER BY denomination DESC
            ''', (transaction_id,))

            denominations = [dict(row) for row in cursor.fetchall()]
            transaction['denominations'] = denominations

        conn.close()
        return transaction

def show_transaction_form():
    """Show transaction form for buy/sell operations"""
    st.subheader("💸 New Transaction")

    manager = TransactionManager()

    # Transaction type selection
    col1, col2 = st.columns(2)

    with col1:
        transaction_type = st.radio(
            "Transaction Type *",
            options=['BUY', 'SELL'],
            horizontal=True,
            help="BUY: We purchase foreign currency from customer\nSELL: We sell foreign currency to customer"
        )

    with col2:
        if transaction_type == 'BUY':
            st.info("💰 We BUY foreign currency from customer (pay IDR)")
        else:
            st.info("💸 We SELL foreign currency to customer (receive IDR)")

    with st.form("transaction_form"):
        # Customer selection
        st.subheader("👥 Customer Information")

        customer_search = st.text_input(
            "Search Customer",
            placeholder="Type customer name or code...",
            key="customer_search"
        )

        customers = []
        if customer_search:
            customers = manager.search_customers(customer_search)
        else:
            customers = manager.get_all_customers()

        if customers:
            customer_options = {
                f"{c['customer_code']} - {c['full_name']}": c['id']
                for c in customers
            }

            selected_customer = st.selectbox(
                "Select Customer *",
                options=list(customer_options.keys()),
                key="customer_select"
            )

            customer_id = customer_options[selected_customer]
            customer_data = next((c for c in customers if c['id'] == customer_id), None)

            if customer_data:
                # Display customer details
                col3, col4 = st.columns(2)

                with col3:
                    st.write(f"**Code:** {customer_data['customer_code']}")
                    st.write(f"**Name:** {customer_data['full_name']}")

                with col4:
                    if customer_data.get('country'):
                        st.write(f"**Country:** {customer_data['country']}")
                    if customer_data.get('phone'):
                        st.write(f"**Phone:** {customer_data['phone']}")
        else:
            st.warning("No customers found. Please add customers first.")
            return

        # Currency selection
        st.subheader("💱 Currency Information")

        currencies = manager.get_all_currencies()

        if not currencies:
            st.warning("No currencies available. Please add currencies first.")
            return

        currency_options = {
            f"{c['code']} - {c['name']}": c['code']
            for c in currencies
        }

        selected_currency = st.selectbox(
            "Select Currency *",
            options=list(currency_options.keys()),
            key="currency_select"
        )

        currency_code = currency_options[selected_currency]
        currency_data = manager.get_currency_by_code(currency_code)

        if currency_data:
            # Display current rates
            col5, col6 = st.columns(2)

            with col5:
                if transaction_type == 'BUY':
                    rate_to_use = currency_data['buy_rate']
                    rate_label = "Buy Rate"
                else:
                    rate_to_use = currency_data['sell_rate']
                    rate_label = "Sell Rate"

                st.metric(rate_label, format_currency(rate_to_use, 'IDR'))

            with col6:
                spread = currency_data['sell_rate'] - currency_data['buy_rate']
                spread_pct = (spread / currency_data['buy_rate']) * 100
                st.metric("Spread", f"{format_currency(spread, 'IDR')} ({spread_pct:.2f}%)")

        # Amount input
        st.subheader("💰 Amount Details")

        col7, col8 = st.columns(2)

        with col7:
            foreign_amount = st.number_input(
                f"Foreign Amount ({currency_code}) *",
                min_value=0.0,
                step=0.01,
                key="foreign_amount",
                help="Amount in foreign currency"
            )

        with col8:
            if currency_data and foreign_amount > 0:
                rate = currency_data['buy_rate'] if transaction_type == 'BUY' else currency_data['sell_rate']
                idr_amount = manager.calculate_idr_amount(foreign_amount, rate, transaction_type)
                st.metric("IDR Amount", format_currency(idr_amount, 'IDR'))
            else:
                idr_amount = 0.0

        # Notes
        notes = st.text_area(
            "Notes",
            placeholder="Enter any additional notes...",
            key="transaction_notes"
        )

        # Denomination breakdown
        if foreign_amount > 0 and currency_data:
            st.subheader("💵 Denomination Breakdown")

            denominations = show_denomination_input(currency_code, foreign_amount)
            if denominations is None:
                st.error("Please fix denomination breakdown before proceeding")
                return
        else:
            denominations = {}

        submitted = st.form_submit_button(
            f"💰 Process {transaction_type} Transaction",
            use_container_width=True,
            type="primary"
        )

        if submitted:
            # Validation
            if not customer_id or not currency_code or foreign_amount <= 0:
                show_error_message("All required fields must be filled")
                return

            if not denominations:
                show_error_message("Denomination breakdown is required")
                return

            # Validate inventory for SELL transactions
            if transaction_type == 'SELL':
                if not manager.validate_inventory(currency_code, denominations, transaction_type):
                    return

            # Prepare transaction data
            transaction_data = {
                'transaction_type': transaction_type,
                'customer_id': customer_id,
                'currency_code': currency_code,
                'foreign_amount': foreign_amount,
                'rate': rate,
                'idr_amount': idr_amount,
                'denominations': denominations,
                'notes': notes if notes else None,
                'total_notes': sum(denominations.values())
            }

            # Process transaction
            with show_loading_spinner("Processing transaction..."):
                transaction_id = manager.process_transaction(transaction_data)

                if transaction_id:
                    st.success(f"Transaction completed successfully!")
                    st.session_state.show_receipt = transaction_id
                    st.rerun()

def show_transaction_history():
    """Display transaction history with filters"""
    st.subheader("📜 Transaction History")

    manager = TransactionManager()

    # Date range filter
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now().date() - timedelta(days=30),
            key="history_start_date"
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now().date(),
            key="history_end_date"
        )

    # Additional filters
    col3, col4, col5 = st.columns(3)

    with col3:
        customers = manager.get_all_customers()
        customer_options = {"All Customers": None}
        customer_options.update({
            f"{c['customer_code']} - {c['full_name']}": c['id'] for c in customers
        })
        selected_customer = st.selectbox(
            "Filter by Customer",
            options=list(customer_options.keys()),
            key="history_customer_filter"
        )

    with col4:
        currencies = manager.get_all_currencies()
        currency_options = {"All Currencies": None}
        currency_options.update({
            f"{c['code']} - {c['name']}": c['code'] for c in currencies
        })
        selected_currency = st.selectbox(
            "Filter by Currency",
            options=list(currency_options.keys()),
            key="history_currency_filter"
        )

    with col5:
        transaction_types = ["All Types", "BUY", "SELL"]
        selected_type = st.selectbox(
            "Filter by Type",
            options=transaction_types,
            key="history_type_filter"
        )

    if st.button("🔍 Apply Filters", key="apply_filters"):
        customer_id = customer_options[selected_customer]
        currency_code = currency_options[selected_currency]
        transaction_type = selected_type if selected_type != "All Types" else None

        with show_loading_spinner("Loading transactions..."):
            transactions = manager.get_transaction_history(
                start_date, end_date, customer_id, currency_code
            )

            if transaction_type:
                transactions = [t for t in transactions if t['transaction_type'] == transaction_type]

            display_transactions(transactions)

def display_transactions(transactions: List[Dict]):
    """Display transactions in a formatted table"""
    if not transactions:
        show_info_message("No transactions found matching the criteria")
        return

    # Convert to DataFrame
    df = pd.DataFrame(transactions)

    # Summary statistics
    st.subheader("📊 Transaction Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Transactions", len(transactions))

    with col2:
        total_buy = len([t for t in transactions if t['transaction_type'] == 'BUY'])
        st.metric("Buy Transactions", total_buy)

    with col3:
        total_sell = len([t for t in transactions if t['transaction_type'] == 'SELL'])
        st.metric("Sell Transactions", total_sell)

    with col4:
        total_idr = sum(t['idr_amount'] for t in transactions)
        st.metric("Total IDR Volume", format_currency(total_idr, 'IDR'))

    # Transaction list
    st.subheader("📋 Transaction Details")

    # Format for display
    df['idr_formatted'] = df['idr_amount'].apply(lambda x: format_currency(x, 'IDR'))
    df['foreign_formatted'] = df.apply(
        lambda row: f"{format_currency(row['foreign_amount'], row['currency_code'])} ({row['symbol']})",
        axis=1
    )
    df['type_emoji'] = df['transaction_type'].apply(lambda x: '💰' if x == 'BUY' else '💸')

    display_columns = [
        'transaction_number', 'type_emoji', 'customer_name', 'currency_name',
        'foreign_formatted', 'rate', 'idr_formatted', 'user_name', 'transaction_date'
    ]
    df_display = df[display_columns].copy()
    df_display.columns = [
        'Transaction #', 'Type', 'Customer', 'Currency',
        'Foreign Amount', 'Rate', 'IDR Amount', 'Cashier', 'Date'
    ]

    create_data_table(df_display, "Transactions")

    # Action buttons
    if transactions:
        st.subheader("🔧 Transaction Actions")

        selected_transaction = st.selectbox(
            "Select transaction for actions:",
            options=[f"{t['transaction_number']} - {t['customer_name']} ({t['transaction_type']})"
                    for t in transactions],
            key="transaction_action_select"
        )

        if selected_transaction:
            transaction_number = selected_transaction.split(' - ')[0]
            transaction_data = next((t for t in transactions if t['transaction_number'] == transaction_number), None)

            if transaction_data:
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("🧾 View Receipt", key=f"receipt_{transaction_number}"):
                        st.session_state.show_receipt = transaction_data['id']
                        st.rerun()

                with col2:
                    if st.button("👁️ View Details", key=f"details_{transaction_number}"):
                        st.session_state.view_transaction = transaction_data['id']
                        st.rerun()

                with col3:
                    if st.button("🖨️ Print", key=f"print_{transaction_number}"):
                        show_info_message("Print functionality would be implemented here")

def show_transaction_receipt(transaction_id: int):
    """Display detailed transaction receipt"""
    manager = TransactionManager()
    transaction = manager.get_transaction_details(transaction_id)

    if not transaction:
        show_error_message("Transaction not found")
        return

    st.subheader(f"🧾 Transaction Receipt - {transaction['transaction_number']}")

    # Receipt layout
    receipt_col1, receipt_col2 = st.columns([2, 1])

    with receipt_col1:
        st.markdown("### 🏦 MONEY CHANGER RECEIPT")
        st.markdown("---")

        # Transaction details
        st.markdown("#### 📋 Transaction Details")
        col1, col2 = st.columns(2)

        with col1:
            st.write(f"**Transaction #:** {transaction['transaction_number']}")
            st.write(f"**Date:** {transaction['transaction_date']}")
            st.write(f"**Type:** {transaction['transaction_type']}")
            st.write(f"**Cashier:** {transaction['user_name']}")

        with col2:
            st.write(f"**Currency:** {transaction['currency_code']} ({transaction['symbol']})")
            st.write(f"**Rate:** {format_number(transaction['rate'])}")
            st.write(f"**Status:** {transaction['status']}")

        st.markdown("---")

        # Customer details
        st.markdown("#### 👥 Customer Information")
        col3, col4 = st.columns(2)

        with col3:
            st.write(f"**Name:** {transaction['customer_name']}")
            st.write(f"**Code:** {transaction['customer_code']}")

        with col4:
            if transaction.get('identity_number'):
                st.write(f"**ID:** {transaction['identity_number']}")
            if transaction.get('country'):
                st.write(f"**Country:** {transaction['country']}")

        st.markdown("---")

        # Financial details
        st.markdown("#### 💰 Financial Details")
        col5, col6 = st.columns(2)

        with col5:
            foreign_display = f"{format_currency(transaction['foreign_amount'], transaction['currency_code'])} ({transaction['symbol']})"
            st.write(f"**Foreign Amount:** {foreign_display}")
            st.write(f"**Rate:** {format_number(transaction['rate'])}")

        with col6:
            st.write(f"**IDR Amount:** {format_currency(transaction['idr_amount'], 'IDR')}")
            if transaction.get('total_notes'):
                st.write(f"**Total Notes:** {transaction['total_notes']}")

    with receipt_col2:
        st.markdown("#### 💵 Denominations")
        if transaction.get('denominations'):
            for denom in transaction['denominations']:
                amount = denom['denomination'] * denom['quantity']
                st.write(f"{transaction['symbol']}{format_number(denom['denomination'], 0)} x {denom['quantity']} = {format_currency(amount, transaction['currency_code'])}")
        else:
            st.write("No denomination details available")

        if transaction.get('notes'):
            st.markdown("---")
            st.markdown("#### 📝 Notes")
            st.write(transaction['notes'])

    st.markdown("---")
    st.markdown("**Thank you for your business!**")

    # Action buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🖨️ Print Receipt", key="print_receipt"):
            show_info_message("Print functionality would be implemented here")

    with col2:
        if st.button("📧 Email Receipt", key="email_receipt"):
            show_info_message("Email functionality would be implemented here")

    with col3:
        if st.button("🔙 Back to List", key="back_from_receipt"):
            st.session_state.show_receipt = None
            st.rerun()

def main():
    """Main function for transaction processing module"""
    # Page configuration
    st.set_page_config(
        page_title="Transaction Processing - Money Changer",
        page_icon="💸",
        layout="wide"
    )

    # Check authentication and permissions
    if not SessionManager.is_authenticated():
        st.error("Please login to access this page")
        return

    if not RoleManager.has_permission('process_transactions'):
        st.error("You don't have permission to process transactions")
        return

    # Page header
    st.title("💸 Transaction Processing")
    st.markdown("Process buy/sell foreign currency transactions")

    # Initialize session state
    if 'show_receipt' not in st.session_state:
        st.session_state.show_receipt = None
    if 'view_transaction' not in st.session_state:
        st.session_state.view_transaction = None

    # Handle receipt display
    if st.session_state.show_receipt:
        show_transaction_receipt(st.session_state.show_receipt)
        return

    # Create tabs
    tab1, tab2 = st.tabs(["💸 New Transaction", "📜 Transaction History"])

    with tab1:
        show_transaction_form()

    with tab2:
        show_transaction_history()

if __name__ == "__main__":
    main()