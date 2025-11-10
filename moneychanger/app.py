"""
Money Changer Application - Main Streamlit Application
Complete money exchange management system with multi-role access control
"""

import streamlit as st
import sys
import os
from datetime import datetime, date

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'database'))

# Initialize database
from database.schema import db, DatabaseSchema
from database.seed_data import seed_all_data

# Import utilities
from utils.auth import SessionManager, AuthUI, Authentication, RoleManager
from utils.helpers import get_session_info, format_currency

# Import page modules
# Note: These will be imported as needed to avoid circular imports

# Initialize database on first run
@st.cache_resource
def init_database():
    """Initialize database and seed with default data"""
    try:
        # Check if database exists and has data
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        conn.close()

        if user_count == 0:
            # Seed the database with initial data
            seed_all_data()
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        return False

def show_dashboard():
    """Show main dashboard with key metrics and overview"""
    st.title("📊 Money Changer Dashboard")
    st.markdown("Welcome to the Money Changer Management System")

    user = get_session_info()
    if user['full_name']:
        st.markdown(f"### 👋 Welcome, {user['full_name']}!")
        st.markdown(f"**Role:** {user['role']}")

    # Initialize session state for dashboard
    if 'dashboard_date' not in st.session_state:
        st.session_state.dashboard_date = datetime.now().date()

    # Date selector for dashboard
    selected_date = st.date_input(
        "Select Date for Dashboard",
        value=st.session_state.dashboard_date,
        key="dashboard_date_selector"
    )

    if selected_date != st.session_state.dashboard_date:
        st.session_state.dashboard_date = selected_date
        st.rerun()

    try:
        # Get dashboard data
        conn = db.get_connection()
        cursor = conn.cursor()

        # Daily transaction summary
        cursor.execute('''
            SELECT
                COUNT(*) as total_transactions,
                COUNT(CASE WHEN transaction_type = 'BUY' THEN 1 END) as buy_transactions,
                COUNT(CASE WHEN transaction_type = 'SELL' THEN 1 END) as sell_transactions,
                SUM(CASE WHEN transaction_type = 'BUY' THEN idr_amount ELSE 0 END) as total_buy_idr,
                SUM(CASE WHEN transaction_type = 'SELL' THEN idr_amount ELSE 0 END) as total_sell_idr,
                SUM(foreign_amount) as total_foreign_amount
            FROM transactions
            WHERE DATE(transaction_date) = ? AND status = 'COMPLETED'
        ''', (selected_date,))

        daily_summary = dict(cursor.fetchone())

        # Currency inventory summary
        cursor.execute('''
            SELECT
                COUNT(DISTINCT di.currency_code) as active_currencies,
                COUNT(*) as total_denominations,
                SUM(di.quantity * di.denomination * c.buy_rate) as total_inventory_value
            FROM denomination_inventory di
            JOIN currencies c ON di.currency_code = c.code
            WHERE di.quantity > 0 AND c.is_active = 1
        ''')

        inventory_summary = dict(cursor.fetchone())

        # Customer count
        cursor.execute('''
            SELECT COUNT(*) as total_customers FROM customers WHERE is_active = 1
        ''')

        customer_count = dict(cursor.fetchone())['total_customers']

        # Recent transactions
        cursor.execute('''
            SELECT t.transaction_number, t.transaction_type, t.foreign_amount,
                   t.currency_code, t.idr_amount, c.full_name as customer_name,
                   t.transaction_date
            FROM transactions t
            JOIN customers c ON t.customer_id = c.id
            WHERE DATE(t.transaction_date) = ? AND t.status = 'COMPLETED'
            ORDER BY t.transaction_date DESC
            LIMIT 10
        ''', (selected_date,))

        recent_transactions = [dict(row) for row in cursor.fetchall()]

        # Low stock alerts
        cursor.execute('''
            SELECT di.currency_code, di.denomination, di.quantity, c.name as currency_name
            FROM denomination_inventory di
            JOIN currencies c ON di.currency_code = c.code
            WHERE di.quantity <= 10 AND c.is_active = 1
            ORDER BY di.quantity
            LIMIT 10
        ''')

        low_stock_items = [dict(row) for row in cursor.fetchall()]

        conn.close()

        # Display dashboard metrics
        st.markdown("## 📈 Today's Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Transactions",
                f"{daily_summary['total_transactions']:,}",
                delta="Today's Activity"
            )

        with col2:
            net_revenue = daily_summary['total_sell_idr'] - daily_summary['total_buy_idr']
            st.metric(
                "Net Revenue",
                format_currency(net_revenue, 'IDR'),
                delta_color="normal" if net_revenue >= 0 else "inverse"
            )

        with col3:
            st.metric(
                "Active Customers",
                f"{customer_count:,}"
            )

        with col4:
            st.metric(
                "Inventory Value",
                format_currency(inventory_summary.get('total_inventory_value', 0), 'IDR')
            )

        # Transaction breakdown
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Buy Transactions",
                f"{daily_summary['buy_transactions']:,}"
            )

        with col2:
            st.metric(
                "Sell Transactions",
                f"{daily_summary['sell_transactions']:,}"
            )

        # Charts and tables
        st.markdown("## 📊 Detailed Analytics")

        tab1, tab2, tab3 = st.tabs(["📋 Recent Transactions", "⚠️ Low Stock Alerts", "💱 Currency Activity"])

        with tab1:
            st.subheader("📋 Recent Transactions")
            if recent_transactions:
                import pandas as pd

                df = pd.DataFrame(recent_transactions)
                df['amount_formatted'] = df.apply(
                    lambda row: f"{format_currency(row['foreign_amount'], row['currency_code'])} ({row['currency_code']})",
                    axis=1
                )
                df['idr_formatted'] = df['idr_amount'].apply(lambda x: format_currency(x, 'IDR'))

                display_df = df[['transaction_number', 'transaction_type', 'customer_name',
                                'amount_formatted', 'idr_formatted', 'transaction_date']]
                display_df.columns = ['Transaction #', 'Type', 'Customer', 'Foreign Amount', 'IDR Amount', 'Time']

                st.dataframe(display_df, use_container_width=True)
            else:
                st.info("No transactions found for selected date")

        with tab2:
            st.subheader("⚠️ Low Stock Alerts")
            if low_stock_items:
                df = pd.DataFrame(low_stock_items)
                df['denomination_formatted'] = df.apply(
                    lambda row: f"{row['currency_code']} {row['denomination']:.0f}",
                    axis=1
                )

                display_df = df[['currency_code', 'denomination_formatted', 'quantity', 'currency_name']]
                display_df.columns = ['Currency', 'Denomination', 'Quantity', 'Name']

                st.dataframe(display_df, use_container_width=True)

                if RoleManager.has_permission('manage_inventory'):
                    if st.button("🔧 Manage Inventory", key="manage_inventory_from_dashboard"):
                        st.switch_page("pages/inventory.py")
            else:
                st.success("✅ All items are well stocked!")

        with tab3:
            st.subheader("💱 Currency Activity")
            try:
                cursor = db.get_connection().cursor()

                cursor.execute('''
                    SELECT t.currency_code, c.name, COUNT(*) as transaction_count,
                           SUM(t.idr_amount) as total_volume
                    FROM transactions t
                    JOIN currencies c ON t.currency_code = c.code
                    WHERE DATE(t.transaction_date) = ? AND t.status = 'COMPLETED'
                    GROUP BY t.currency_code, c.name
                    ORDER BY total_volume DESC
                ''', (selected_date,))

                currency_activity = [dict(row) for row in cursor.fetchall()]
                cursor.connection.close()

                if currency_activity:
                    df = pd.DataFrame(currency_activity)
                    df['volume_formatted'] = df['total_volume'].apply(lambda x: format_currency(x, 'IDR'))

                    display_df = df[['currency_code', 'name', 'transaction_count', 'volume_formatted']]
                    display_df.columns = ['Code', 'Currency', 'Transactions', 'Total Volume']

                    st.dataframe(display_df, use_container_width=True)

                    # Simple pie chart
                    import plotly.express as px

                    fig = px.pie(
                        df,
                        values='total_volume',
                        names='currency_code',
                        title='Transaction Volume by Currency'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No currency activity for selected date")

            except Exception as e:
                st.error(f"Error loading currency activity: {e}")

        # Quick actions based on role
        st.markdown("## 🚀 Quick Actions")

        if RoleManager.has_permission('process_transactions'):
            col1, col2 = st.columns(2)

            with col1:
                if st.button("💸 New Transaction", use_container_width=True, type="primary"):
                    st.switch_page("pages/transactions.py")

            with col2:
                if st.button("📜 Transaction History", use_container_width=True):
                    st.switch_page("pages/transaction_history.py")

        if RoleManager.has_permission('manage_currencies'):
            if st.button("💱 Update Exchange Rates", use_container_width=True):
                st.switch_page("pages/currencies.py")

        if RoleManager.has_permission('view_reports'):
            if st.button("📊 View Reports", use_container_width=True):
                st.switch_page("pages/reports.py")

    except Exception as e:
        st.error(f"Error loading dashboard data: {e}")
        st.info("Please check your database connection and try again.")

def show_login_page():
    """Show login page"""
    # Page configuration for login
    st.set_page_config(
        page_title="Money Changer - Login",
        page_icon="🏦",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # Hide sidebar for login page
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # Login form
    st.markdown("# 🏦 Money Changer System")
    st.markdown("## Foreign Exchange Management System")
    st.markdown("---")

    AuthUI.show_login_form()

    # Additional information
    st.markdown("---")
    st.markdown("### 👤 Default Login Credentials")
    st.markdown("**For demonstration purposes:**")
    st.markdown("- **Admin:** `admin` / `admin123`")
    st.markdown("- **Cashier:** `cashier1` / `cashier123`")
    st.markdown("- **Auditor:** `auditor1` / `auditor123`")

    st.markdown("---")
    st.markdown("### 🔐 System Features")
    st.markdown("- 💱 **Multi-Currency Support** - Manage multiple foreign currencies")
    st.markdown("- 💰 **Transaction Processing** - Buy and sell foreign currencies")
    st.markdown("- 📊 **Real-time Inventory** - Track currency denominations")
    st.markdown("- 📋 **Comprehensive Reports** - Financial and business analytics")
    st.markdown("- 👥 **Multi-Role Access** - Admin, Cashier, and Auditor roles")
    st.markdown("- 🔍 **Audit Trail** - Complete activity tracking")

def main():
    """Main application function"""
    # Initialize session state
    SessionManager.init_session_state()

    # Initialize database
    if st.session_state.get('db_initialized', False) is False:
        with st.spinner("Initializing database..."):
            init_database()
            st.session_state.db_initialized = True

    # Check authentication
    if not SessionManager.is_authenticated():
        show_login_page()
        return

    # Main application
    # Configure page
    st.set_page_config(
        page_title="Money Changer - Dashboard",
        page_icon="🏦",
        layout="wide"
    )

    # Show sidebar with navigation and logout
    AuthUI.show_logout_button()
    AuthUI.show_navigation_menu()

    # Main content area
    show_dashboard()

    # Footer
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #666; font-size: 0.8em;'>"
        f"© 2024 Money Changer System | Powered by Streamlit | "
        f"Last login: {SessionManager.get_current_user().get('full_name', 'Unknown') if SessionManager.get_current_user() else 'N/A'}"
        f"</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()