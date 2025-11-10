"""
Currency Management Module for Money Changer Application
Handles currency CRUD operations, rate updates, and rate history
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Optional
import plotly.express as px
import plotly.graph_objects as go

# Import database models and utilities
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import currency_model, db
from utils.auth import SessionManager, RoleManager, require_permission
from utils.helpers import (
    format_currency, format_number, show_success_message, show_error_message,
    show_info_message, create_data_table, validate_positive_number
)

class CurrencyManager:
    """Currency management class"""

    def __init__(self):
        self.model = currency_model

    def get_all_currencies(self) -> List[Dict]:
        """Get all active currencies"""
        return self.model.get_all_currencies()

    def get_currency_by_code(self, code: str) -> Optional[Dict]:
        """Get currency by code"""
        return self.model.get_currency_by_code(code)

    def create_currency(self, code: str, name: str, symbol: str,
                       buy_rate: float, sell_rate: float) -> bool:
        """Create a new currency"""
        try:
            self.model.create_currency(code, name, symbol, buy_rate, sell_rate)
            return True
        except Exception as e:
            show_error_message(f"Failed to create currency: {str(e)}")
            return False

    def update_rates(self, code: str, buy_rate: float, sell_rate: float) -> bool:
        """Update currency rates"""
        try:
            user = SessionManager.get_current_user()
            success = self.model.update_rates(
                code, buy_rate, sell_rate, user['id'] if user else None
            )
            if success:
                show_success_message(f"Rates updated for {code}")
            return success
        except Exception as e:
            show_error_message(f"Failed to update rates: {str(e)}")
            return False

    def get_rate_history(self, code: str, days: int = 30) -> List[Dict]:
        """Get rate history for a currency"""
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT erh.*, u.full_name as updated_by_name
            FROM exchange_rate_history erh
            LEFT JOIN users u ON erh.updated_by = u.id
            WHERE erh.currency_code = ?
            AND erh.updated_at >= datetime('now', '-{} days')
            ORDER BY erh.updated_at DESC
        '''.format(days), (code.upper(),))

        history = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return history

def show_currency_form(currency_data: Optional[Dict] = None):
    """Show currency creation/edit form"""
    is_edit = currency_data is not None
    title = "Edit Currency" if is_edit else "Add New Currency"

    st.subheader(f"💱 {title}")

    with st.form("currency_form"):
        col1, col2 = st.columns(2)

        with col1:
            code = st.text_input(
                "Currency Code *",
                value=currency_data['code'] if is_edit else "",
                placeholder="e.g., USD",
                disabled=is_edit
            ).upper()

            name = st.text_input(
                "Currency Name *",
                value=currency_data['name'] if is_edit else "",
                placeholder="e.g., United States Dollar"
            )

        with col2:
            symbol = st.text_input(
                "Symbol *",
                value=currency_data['symbol'] if is_edit else "",
                placeholder="e.g., $"
            )

        st.markdown("### Exchange Rates (IDR)")

        col3, col4 = st.columns(2)

        with col3:
            buy_rate = st.number_input(
                "Buy Rate *",
                value=float(currency_data['buy_rate']) if is_edit else 0.0,
                min_value=0.0,
                step=0.01,
                help="Rate at which we buy foreign currency"
            )

        with col4:
            sell_rate = st.number_input(
                "Sell Rate *",
                value=float(currency_data['sell_rate']) if is_edit else 0.0,
                min_value=0.0,
                step=0.01,
                help="Rate at which we sell foreign currency"
            )

        # Validation
        if buy_rate <= 0:
            show_error_message("Buy rate must be positive")
        if sell_rate <= 0:
            show_error_message("Sell rate must be positive")
        if buy_rate >= sell_rate:
            show_error_message("Sell rate should be higher than buy rate")

        submitted = st.form_submit_button(
            "💾 Save Currency" if not is_edit else "💾 Update Currency",
            use_container_width=True
        )

        if submitted:
            if not code or not name or not symbol:
                show_error_message("All fields marked with * are required")
                return

            if buy_rate <= 0 or sell_rate <= 0:
                show_error_message("Rates must be positive")
                return

            if buy_rate >= sell_rate:
                show_error_message("Sell rate should be higher than buy rate")
                return

            manager = CurrencyManager()

            if is_edit:
                success = manager.update_rates(code, buy_rate, sell_rate)
            else:
                success = manager.create_currency(code, name, symbol, buy_rate, sell_rate)

            if success:
                show_success_message(
                    f"Currency {'updated' if is_edit else 'created'} successfully!"
                )
                st.rerun()

def show_rate_update_form():
    """Show quick rate update form"""
    st.subheader("🔄 Quick Rate Update")

    manager = CurrencyManager()
    currencies = manager.get_all_currencies()

    if not currencies:
        show_info_message("No currencies available for rate update")
        return

    with st.form("rate_update_form"):
        # Currency selection
        currency_options = {f"{c['code']} - {c['name']}": c['code'] for c in currencies}
        selected_currency = st.selectbox(
            "Select Currency *",
            options=list(currency_options.keys()),
            help="Choose currency to update rates"
        )

        currency_code = currency_options[selected_currency]
        current_currency = manager.get_currency_by_code(currency_code)

        # Show current rates
        if current_currency:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Current Buy Rate", format_currency(current_currency['buy_rate'], 'IDR'))
            with col2:
                st.metric("Current Sell Rate", format_currency(current_currency['sell_rate'], 'IDR'))

        st.markdown("### New Rates")

        col3, col4 = st.columns(2)

        with col3:
            new_buy_rate = st.number_input(
                "New Buy Rate *",
                value=float(current_currency['buy_rate']) if current_currency else 0.0,
                min_value=0.0,
                step=0.01
            )

        with col4:
            new_sell_rate = st.number_input(
                "New Sell Rate *",
                value=float(current_currency['sell_rate']) if current_currency else 0.0,
                min_value=0.0,
                step=0.01
            )

        # Calculate spread
        if new_buy_rate > 0 and new_sell_rate > 0:
            spread = new_sell_rate - new_buy_rate
            spread_percentage = (spread / new_buy_rate) * 100
            st.info(f"💰 Spread: {format_currency(spread, 'IDR')} ({spread_percentage:.2f}%)")

        submitted = st.form_submit_button("🔄 Update Rates", use_container_width=True)

        if submitted:
            if new_buy_rate <= 0 or new_sell_rate <= 0:
                show_error_message("Rates must be positive")
                return

            if new_buy_rate >= new_sell_rate:
                show_error_message("Sell rate should be higher than buy rate")
                return

            success = manager.update_rates(currency_code, new_buy_rate, new_sell_rate)

            if success:
                show_success_message(f"Rates updated for {currency_code}")
                st.rerun()

def show_currency_list():
    """Display list of currencies with management options"""
    st.subheader("📊 Currency List")

    manager = CurrencyManager()
    currencies = manager.get_all_currencies()

    if not currencies:
        show_info_message("No currencies found")
        return

    # Convert to DataFrame for display
    df = pd.DataFrame(currencies)

    # Format rates for display
    df['buy_rate_formatted'] = df['buy_rate'].apply(lambda x: format_currency(x, 'IDR'))
    df['sell_rate_formatted'] = df['sell_rate'].apply(lambda x: format_currency(x, 'IDR'))
    df['spread'] = df['sell_rate'] - df['buy_rate']
    df['spread_formatted'] = df['spread'].apply(lambda x: format_currency(x, 'IDR'))

    # Reorder columns
    display_columns = [
        'code', 'name', 'symbol', 'buy_rate_formatted', 'sell_rate_formatted',
        'spread_formatted', 'last_updated'
    ]
    df_display = df[display_columns].copy()
    df_display.columns = [
        'Code', 'Name', 'Symbol', 'Buy Rate', 'Sell Rate', 'Spread', 'Last Updated'
    ]

    create_data_table(df_display, "Active Currencies")

    # Action buttons for each currency
    if RoleManager.has_permission('manage_currencies'):
        st.subheader("🔧 Currency Actions")

        selected_currency = st.selectbox(
            "Select currency for actions:",
            options=[f"{c['code']} - {c['name']}" for c in currencies],
            key="currency_action_select"
        )

        if selected_currency:
            currency_code = selected_currency.split(' - ')[0]
            currency_data = manager.get_currency_by_code(currency_code)

            col1, col2 = st.columns(2)

            with col1:
                if st.button("📝 Edit Rates", key=f"edit_{currency_code}"):
                    st.session_state.edit_currency = currency_data
                    st.rerun()

            with col2:
                if st.button("📈 View History", key=f"history_{currency_code}"):
                    st.session_state.view_history = currency_code
                    st.rerun()

def show_rate_history(currency_code: str):
    """Display rate history for a currency"""
    st.subheader(f"📈 Rate History - {currency_code}")

    manager = CurrencyManager()
    history = manager.get_rate_history(currency_code, days=30)

    if not history:
        show_info_message("No rate history available")
        return

    # Convert to DataFrame
    df = pd.DataFrame(history)

    # Create tabs for different views
    tab1, tab2 = st.tabs(["📊 Chart View", "📋 Table View"])

    with tab1:
        # Create rate history chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df['updated_at'],
            y=df['buy_rate'],
            mode='lines+markers',
            name='Buy Rate',
            line=dict(color='green')
        ))

        fig.add_trace(go.Scatter(
            x=df['updated_at'],
            y=df['sell_rate'],
            mode='lines+markers',
            name='Sell Rate',
            line=dict(color='red')
        ))

        fig.update_layout(
            title=f"Exchange Rate History - {currency_code}",
            xaxis_title="Date",
            yaxis_title="Rate (IDR)",
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Format for table display
        df['buy_rate_formatted'] = df['buy_rate'].apply(lambda x: format_currency(x, 'IDR'))
        df['sell_rate_formatted'] = df['sell_rate'].apply(lambda x: format_currency(x, 'IDR'))
        df['spread_formatted'] = (df['sell_rate'] - df['buy_rate']).apply(lambda x: format_currency(x, 'IDR'))

        display_columns = [
            'updated_at', 'buy_rate_formatted', 'sell_rate_formatted',
            'spread_formatted', 'updated_by_name'
        ]
        df_display = df[display_columns].copy()
        df_display.columns = [
            'Date & Time', 'Buy Rate', 'Sell Rate', 'Spread', 'Updated By'
        ]

        create_data_table(df_display, "Rate History")

def show_currency_statistics():
    """Show currency statistics and analytics"""
    st.subheader("📊 Currency Statistics")

    manager = CurrencyManager()
    currencies = manager.get_all_currencies()

    if not currencies:
        show_info_message("No currencies available for statistics")
        return

    # Convert to DataFrame
    df = pd.DataFrame(currencies)

    # Calculate statistics
    total_currencies = len(df)
    avg_buy_rate = df['buy_rate'].mean()
    avg_sell_rate = df['sell_rate'].mean()
    avg_spread = (df['sell_rate'] - df['buy_rate']).mean()

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Currencies", total_currencies)

    with col2:
        st.metric("Avg Buy Rate", format_currency(avg_buy_rate, 'IDR'))

    with col3:
        st.metric("Avg Sell Rate", format_currency(avg_sell_rate, 'IDR'))

    with col4:
        st.metric("Avg Spread", format_currency(avg_spread, 'IDR'))

    # Spread analysis
    st.subheader("💰 Spread Analysis")

    df['spread'] = df['sell_rate'] - df['buy_rate']
    df['spread_percentage'] = (df['spread'] / df['buy_rate']) * 100

    # Sort by spread
    df_sorted = df.sort_values('spread_percentage', ascending=False)

    # Create spread chart
    fig = px.bar(
        df_sorted,
        x='code',
        y='spread_percentage',
        title='Spread Percentage by Currency',
        labels={'code': 'Currency Code', 'spread_percentage': 'Spread (%)'}
    )
    st.plotly_chart(fig, use_container_width=True)

    # Spread table
    df['spread_formatted'] = df['spread'].apply(lambda x: format_currency(x, 'IDR'))
    display_columns = ['code', 'name', 'buy_rate', 'sell_rate', 'spread_formatted', 'spread_percentage']
    df_display = df[display_columns].copy()
    df_display.columns = ['Code', 'Name', 'Buy Rate', 'Sell Rate', 'Spread', 'Spread %']

    create_data_table(df_display, "Currency Spreads")

def main():
    """Main function for currency management module"""
    # Page configuration
    st.set_page_config(
        page_title="Currency Management - Money Changer",
        page_icon="💱",
        layout="wide"
    )

    # Check authentication and permissions
    if not SessionManager.is_authenticated():
        st.error("Please login to access this page")
        return

    if not RoleManager.has_permission('manage_currencies'):
        st.error("You don't have permission to access currency management")
        return

    # Page header
    st.title("💱 Currency Management")
    st.markdown("Manage exchange rates and currency information")

    # Initialize session state
    if 'edit_currency' not in st.session_state:
        st.session_state.edit_currency = None
    if 'view_history' not in st.session_state:
        st.session_state.view_history = None

    # Handle edit mode
    if st.session_state.edit_currency:
        show_currency_form(st.session_state.edit_currency)
        if st.button("❌ Cancel Edit"):
            st.session_state.edit_currency = None
            st.rerun()
        return

    # Handle history view
    if st.session_state.view_history:
        show_rate_history(st.session_state.view_history)
        if st.button("🔙 Back to List"):
            st.session_state.view_history = None
            st.rerun()
        return

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Currency List", "➕ Add Currency", "🔄 Quick Update", "📊 Statistics"
    ])

    with tab1:
        show_currency_list()

    with tab2:
        show_currency_form()

    with tab3:
        show_rate_update_form()

    with tab4:
        show_currency_statistics()

if __name__ == "__main__":
    main()