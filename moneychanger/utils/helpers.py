"""
Utility functions and helpers for Money Changer application
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64

def format_currency(amount: float, currency_code: str = "IDR") -> str:
    """Format currency amount with proper formatting"""
    if amount is None:
        return "0.00"

    # Currency symbols
    symbols = {
        'IDR': 'Rp',
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'SGD': 'S$',
        'AUD': 'A$',
        'MYR': 'RM',
        'CNY': '¥',
        'SAR': '﷼',
        'THB': '฿'
    }

    symbol = symbols.get(currency_code, '')

    if currency_code == 'IDR':
        return f"{symbol}{amount:,.0f}"
    else:
        return f"{symbol}{amount:,.2f}"

def format_number(amount: float, decimal_places: int = 2) -> str:
    """Format number with thousand separators"""
    if amount is None:
        return "0"

    return f"{amount:,.{decimal_places}f}"

def parse_amount(amount_str: str) -> Optional[float]:
    """Parse amount string to float, handling various formats"""
    if not amount_str:
        return None

    try:
        # Remove common currency symbols and formatting
        cleaned = amount_str.replace(',', '').replace('$', '').replace('€', '').replace('£', '').replace('¥', '').replace('Rp', '').strip()
        return float(cleaned)
    except ValueError:
        return None

def validate_positive_number(value: str, field_name: str) -> Optional[float]:
    """Validate and convert positive number"""
    try:
        num = float(value)
        if num <= 0:
            st.error(f"{field_name} must be positive")
            return None
        return num
    except ValueError:
        st.error(f"Invalid {field_name}. Please enter a valid number.")
        return None

def show_success_message(message: str):
    """Show success message with consistent styling"""
    st.success(f"✅ {message}")

def show_error_message(message: str):
    """Show error message with consistent styling"""
    st.error(f"❌ {message}")

def show_info_message(message: str):
    """Show info message with consistent styling"""
    st.info(f"ℹ️ {message}")

def show_warning_message(message: str):
    """Show warning message with consistent styling"""
    st.warning(f"⚠️ {message}")

def create_data_table(df: pd.DataFrame, title: str = "", use_container_width: bool = True):
    """Create styled data table with title"""
    if title:
        st.subheader(title)

    if df.empty:
        show_warning_message("No data available")
        return

    # Format numeric columns
    for col in df.select_dtypes(include=['float64', 'int64']).columns:
        if 'rate' in col.lower() or 'amount' in col.lower():
            df[col] = df[col].apply(lambda x: format_currency(x, 'IDR') if 'idr' in col.lower() else format_number(x))

    st.dataframe(df, use_container_width=use_container_width)

def create_metric_card(title: str, value: str, delta: Optional[str] = None, delta_color: str = "normal"):
    """Create metric card with consistent styling"""
    st.metric(
        label=title,
        value=value,
        delta=delta,
        delta_color=delta_color
    )

def create_date_range_selector(label: str = "Select Date Range") -> tuple:
    """Create date range selector with default values"""
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.datebox(
            "Start Date",
            value=datetime.now().date() - timedelta(days=30),
            key=f"{label}_start"
        )

    with col2:
        end_date = st.datebox(
            "End Date",
            value=datetime.now().date(),
            key=f"{label}_end"
        )

    if start_date > end_date:
        show_error_message("Start date cannot be after end date")
        return None, None

    return start_date, end_date

def export_to_csv(df: pd.DataFrame, filename: str = "export.csv") -> str:
    """Export dataframe to CSV and return download link"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV file</a>'
    return href

def export_to_excel(df: pd.DataFrame, filename: str = "export.xlsx") -> bytes:
    """Export dataframe to Excel and return bytes"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
    output.seek(0)
    return output.getvalue()

def create_transaction_chart(data: List[Dict], chart_type: str = "bar") -> go.Figure:
    """Create transaction chart based on data type"""
    if not data:
        return go.Figure()

    df = pd.DataFrame(data)

    if chart_type == "daily_transactions":
        fig = px.bar(
            df,
            x='date',
            y='transaction_count',
            title='Daily Transaction Count',
            labels={'date': 'Date', 'transaction_count': 'Number of Transactions'}
        )
    elif chart_type == "revenue_chart":
        fig = px.line(
            df,
            x='date',
            y='total_revenue',
            title='Daily Revenue Trend',
            labels={'date': 'Date', 'total_revenue': 'Revenue (IDR)'}
        )
        fig.update_layout(yaxis_tickformat=',.0f')
    elif chart_type == "currency_distribution":
        fig = px.pie(
            df,
            values='total_amount',
            names='currency_code',
            title='Transaction Distribution by Currency'
        )
    else:
        fig = go.Figure()

    return fig

def calculate_profit_loss(buy_amount: float, sell_amount: float, buy_rate: float, sell_rate: float) -> float:
    """Calculate profit/loss from buy and sell transactions"""
    buy_idr = buy_amount * buy_rate
    sell_idr = sell_amount * sell_rate
    return sell_idr - buy_idr

def get_currency_denominations(currency_code: str) -> List[float]:
    """Get standard denominations for a currency"""
    denominations = {
        'USD': [100, 50, 20, 10, 5, 1],
        'EUR': [500, 200, 100, 50, 20, 10, 5],
        'GBP': [50, 20, 10, 5],
        'JPY': [10000, 5000, 2000, 1000],
        'SGD': [1000, 100, 50, 10, 5, 2],
        'AUD': [100, 50, 20, 10, 5],
        'MYR': [100, 50, 20, 10, 5, 1],
        'CNY': [100, 50, 20, 10, 5, 1],
        'SAR': [500, 200, 100, 50, 20, 10, 5, 1],
        'THB': [1000, 500, 100, 50, 20]
    }
    return denominations.get(currency_code.upper(), [])

def validate_denomination_input(denominations: Dict[float, int], total_amount: float) -> bool:
    """Validate if denomination breakdown matches total amount"""
    calculated_total = sum(denom * qty for denom, qty in denominations.items())
    return abs(calculated_total - total_amount) < 0.01  # Allow for floating point precision

def show_denomination_input(currency_code: str, total_amount: float) -> Optional[Dict[float, int]]:
    """Show denomination input interface"""
    st.subheader("💵 Denomination Breakdown")

    denominations = get_currency_denominations(currency_code)
    if not denominations:
        st.warning("No standard denominations available for this currency")
        return None

    st.write(f"Total amount: **{format_currency(total_amount, currency_code)}**")

    denom_inputs = {}
    remaining_amount = total_amount

    for denom in sorted(denominations, reverse=True):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.write(f"{currency_code} {format_number(denom, 0)}")

        with col2:
            max_possible = int(remaining_amount // denom)
            quantity = st.number_input(
                "Qty",
                min_value=0,
                max_value=max_possible,
                value=0,
                key=f"denom_{denom}",
                label_visibility="collapsed"
            )
        denom_inputs[denom] = quantity

        with col3:
            subtotal = quantity * denom
            st.write(f"= {format_currency(subtotal, currency_code)}")
            remaining_amount -= subtotal

    # Validation
    calculated_total = sum(denom * qty for denom, qty in denom_inputs.items())
    difference = total_amount - calculated_total

    if abs(difference) < 0.01:
        show_success_message("Denomination breakdown is correct!")
        return denom_inputs
    else:
        show_error_message(f"Denomination mismatch: {format_currency(abs(difference), currency_code)} remaining")
        return None

def create_pdf_receipt(transaction_data: Dict) -> bytes:
    """Create PDF receipt for transaction (placeholder)"""
    # In a real implementation, you would use a PDF library like reportlab
    # For now, return a simple text representation
    receipt_text = f"""
    MONEY CHANGER RECEIPT
    =====================

    Transaction Number: {transaction_data.get('transaction_number', 'N/A')}
    Date: {transaction_data.get('transaction_date', 'N/A')}

    Customer: {transaction_data.get('customer_name', 'N/A')}
    Customer Code: {transaction_data.get('customer_code', 'N/A')}

    Transaction Details:
    - Type: {transaction_data.get('transaction_type', 'N/A')}
    - Currency: {transaction_data.get('currency_code', 'N/A')}
    - Amount: {format_currency(transaction_data.get('foreign_amount', 0), transaction_data.get('currency_code', 'USD'))}
    - Rate: {format_number(transaction_data.get('rate', 0))}
    - Total (IDR): {format_currency(transaction_data.get('idr_amount', 0), 'IDR')}

    Cashier: {transaction_data.get('user_name', 'N/A')}

    Thank you for your business!
    """

    return receipt_text.encode('utf-8')

def get_session_info() -> Dict[str, Any]:
    """Get current session information"""
    if hasattr(st.session_state, 'user') and st.session_state.user:
        return {
            'user_id': st.session_state.user.get('id'),
            'username': st.session_state.user.get('username'),
            'full_name': st.session_state.user.get('full_name'),
            'role': st.session_state.user.get('role'),
            'is_authenticated': st.session_state.get('is_authenticated', False)
        }
    return {
        'user_id': None,
        'username': None,
        'full_name': None,
        'role': None,
        'is_authenticated': False
    }

def log_user_action(action: str, details: Dict = None):
    """Log user action for audit trail"""
    try:
        from ..database.models import db
        session_info = get_session_info()

        db.log_audit(
            user_id=session_info.get('user_id'),
            action=action,
            table_name=details.get('table_name') if details else None,
            record_id=details.get('record_id') if details else None,
            new_values=details.get('new_values') if details else None
        )
    except Exception as e:
        # Log errors but don't fail the main function
        print(f"Failed to log user action: {e}")

def show_loading_spinner(text: str = "Loading..."):
    """Show loading spinner with consistent text"""
    return st.spinner(f"⏳ {text}")

def confirmation_dialog(title: str, message: str) -> bool:
    """Show confirmation dialog and return user's choice"""
    if st.button(f"⚠️ {title}", key=f"confirm_{title}"):
        st.warning(message)
        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ Yes, Continue", key=f"confirm_yes_{title}"):
                return True

        with col2:
            if st.button("❌ Cancel", key=f"confirm_no_{title}"):
                return False

    return False