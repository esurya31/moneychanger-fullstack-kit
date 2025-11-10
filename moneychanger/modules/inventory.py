"""
Inventory Management Module for Money Changer Application
Handles denomination stock management, inventory tracking, and stock adjustments
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go

# Import database models and utilities
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import inventory_model, currency_model
from utils.auth import SessionManager, RoleManager, require_permission
from utils.helpers import (
    format_currency, format_number, show_success_message, show_error_message,
    show_info_message, create_data_table, show_loading_spinner, log_user_action
)

class InventoryManager:
    """Inventory management class"""

    def __init__(self):
        self.inventory_model = inventory_model
        self.currency_model = currency_model

    def get_all_inventory(self) -> List[Dict]:
        """Get all inventory with currency information"""
        return self.inventory_model.get_all_inventory()

    def get_inventory_by_currency(self, currency_code: str) -> List[Dict]:
        """Get inventory for specific currency"""
        return self.inventory_model.get_inventory_by_currency(currency_code)

    def get_currency_summary(self) -> List[Dict]:
        """Get inventory summary by currency"""
        return self.inventory_model.get_currency_summary()

    def get_all_currencies(self) -> List[Dict]:
        """Get all active currencies"""
        return self.currency_model.get_all_currencies()

    def update_inventory(self, currency_code: str, denomination: float,
                        quantity_change: int, reason: str = None) -> bool:
        """Update inventory quantity with audit logging"""
        try:
            user = SessionManager.get_current_user()
            success = self.inventory_model.update_inventory(
                currency_code, denomination, quantity_change,
                user['id'] if user else None
            )

            if success:
                # Log the inventory adjustment
                log_user_action("INVENTORY_ADJUSTMENT", {
                    'table_name': 'denomination_inventory',
                    'new_values': {
                        'currency_code': currency_code,
                        'denomination': denomination,
                        'quantity_change': quantity_change,
                        'reason': reason
                    }
                })

            return success

        except Exception as e:
            show_error_message(f"Failed to update inventory: {str(e)}")
            return False

    def calculate_total_inventory_value(self) -> float:
        """Calculate total inventory value in IDR"""
        inventory = self.get_all_inventory()
        return sum(item.get('idr_value', 0) for item in inventory)

    def get_low_stock_items(self, threshold: int = 10) -> List[Dict]:
        """Get items with low stock"""
        inventory = self.get_all_inventory()
        return [item for item in inventory if item['quantity'] <= threshold]

    def validate_stock_adjustment(self, currency_code: str, denomination: float,
                                 quantity_change: int) -> Tuple[bool, str]:
        """Validate stock adjustment"""
        if not currency_code or not denomination:
            return False, "Currency and denomination are required"

        if quantity_change == 0:
            return False, "Quantity change cannot be zero"

        # Check if current inventory can handle negative adjustment
        if quantity_change < 0:
            current_inventory = self.get_inventory_by_currency(currency_code)
            current_qty = 0

            for item in current_inventory:
                if abs(item['denomination'] - denomination) < 0.01:
                    current_qty = item['quantity']
                    break

            if current_qty + quantity_change < 0:
                return False, f"Insufficient stock. Current: {current_qty}, Adjustment: {quantity_change}"

        return True, "Valid"

def show_inventory_dashboard():
    """Show inventory dashboard with key metrics"""
    st.subheader("📊 Inventory Dashboard")

    manager = InventoryManager()

    # Get inventory data
    all_inventory = manager.get_all_inventory()
    currency_summary = manager.get_currency_summary()
    low_stock_items = manager.get_low_stock_items(threshold=10)

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_currencies = len(currency_summary)
        st.metric("Active Currencies", total_currencies)

    with col2:
        total_denominations = len(all_inventory)
        st.metric("Total Denominations", total_denominations)

    with col3:
        total_value = manager.calculate_total_inventory_value()
        st.metric("Total Value (IDR)", format_currency(total_value, 'IDR'))

    with col4:
        low_stock_count = len(low_stock_items)
        alert_color = "normal" if low_stock_count == 0 else "inverse"
        st.metric("Low Stock Alerts", low_stock_count, delta_color=alert_color)

    # Low stock alerts
    if low_stock_items:
        st.subheader("⚠️ Low Stock Alerts")

        low_stock_df = pd.DataFrame(low_stock_items)
        low_stock_df['formatted_value'] = low_stock_df.apply(
            lambda row: f"{format_currency(row['denomination'], row['currency_code'])} x {row['quantity']}",
            axis=1
        )

        display_columns = ['currency_code', 'denomination', 'quantity', 'formatted_value']
        low_stock_display = low_stock_df[display_columns].copy()
        low_stock_display.columns = ['Currency', 'Denomination', 'Quantity', 'Total Value']

        create_data_table(low_stock_display, "Items Requiring Restock")

    # Currency summary
    if currency_summary:
        st.subheader("💰 Inventory Value by Currency")

        summary_df = pd.DataFrame(currency_summary)

        # Create pie chart
        fig = px.pie(
            summary_df,
            values='total_idr_value',
            names='currency_code',
            title="Inventory Value Distribution",
            hover_data=['total_foreign_amount', 'denomination_count']
        )
        st.plotly_chart(fig, use_container_width=True)

        # Summary table
        summary_df['total_foreign_formatted'] = summary_df.apply(
            lambda row: f"{format_currency(row['total_foreign_amount'], row['currency_code'])}",
            axis=1
        )
        summary_df['total_idr_formatted'] = summary_df['total_idr_value'].apply(
            lambda x: format_currency(x, 'IDR')
        )

        display_columns = ['currency_code', 'currency_name', 'total_foreign_formatted',
                          'total_idr_formatted', 'denomination_count']
        summary_display = summary_df[display_columns].copy()
        summary_display.columns = ['Currency', 'Name', 'Foreign Amount', 'IDR Value', 'Denominations']

        create_data_table(summary_display, "Inventory Summary by Currency")

def show_inventory_by_currency():
    """Show detailed inventory for each currency"""
    st.subheader("💵 Inventory by Currency")

    manager = InventoryManager()
    currencies = manager.get_all_currencies()

    if not currencies:
        show_info_message("No currencies available")
        return

    # Currency selector
    currency_options = {
        f"{c['code']} - {c['name']}": c['code']
        for c in currencies
    }

    selected_currency = st.selectbox(
        "Select Currency",
        options=list(currency_options.keys()),
        key="inventory_currency_select"
    )

    currency_code = currency_options[selected_currency]
    currency_data = manager.currency_model.get_currency_by_code(currency_code)

    # Display currency info
    if currency_data:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Currency", f"{currency_data['code']} ({currency_data['symbol']})")

        with col2:
            st.metric("Buy Rate", format_currency(currency_data['buy_rate'], 'IDR'))

        with col3:
            st.metric("Sell Rate", format_currency(currency_data['sell_rate'], 'IDR'))

    # Get inventory for selected currency
    inventory = manager.get_inventory_by_currency(currency_code)

    if not inventory:
        show_info_message(f"No inventory found for {currency_code}")
        return

    # Convert to DataFrame
    df = pd.DataFrame(inventory)

    # Calculate totals
    total_foreign_amount = sum(item['denomination'] * item['quantity'] for item in inventory)
    total_idr_value = total_foreign_amount * currency_data['buy_rate'] if currency_data else 0

    # Display summary
    col4, col5, col6 = st.columns(3)

    with col4:
        st.metric("Total Denominations", len(inventory))

    with col5:
        total_pieces = sum(item['quantity'] for item in inventory)
        st.metric("Total Pieces", total_pieces)

    with col6:
        st.metric("Total Value (IDR)", format_currency(total_idr_value, 'IDR'))

    # Inventory details table
    st.subheader(f"📋 {currency_code} Denomination Details")

    # Format for display
    df['formatted_denomination'] = df.apply(
        lambda row: f"{currency_data['symbol'] if currency_data else ''}{format_number(row['denomination'], 0)}",
        axis=1
    )
    df['formatted_value'] = df.apply(
        lambda row: f"{format_currency(row['denomination'] * row['quantity'], currency_code)}",
        axis=1
    )
    df['idr_value'] = df.apply(
        lambda row: row['denomination'] * row['quantity'] * (currency_data['buy_rate'] if currency_data else 0),
        axis=1
    )
    df['formatted_idr_value'] = df['idr_value'].apply(lambda x: format_currency(x, 'IDR'))

    display_columns = ['formatted_denomination', 'quantity', 'formatted_value', 'formatted_idr_value', 'last_updated']
    df_display = df[display_columns].copy()
    df_display.columns = ['Denomination', 'Quantity', 'Foreign Value', 'IDR Value', 'Last Updated']

    create_data_table(df_display, f"{currency_code} Inventory Details")

    # Stock adjustment section (for admin users)
    if RoleManager.has_permission('manage_inventory'):
        st.subheader("🔧 Stock Adjustment")

        with st.form("stock_adjustment_form"):
            adjustment_type = st.radio(
                "Adjustment Type",
                options=["Add Stock", "Remove Stock"],
                horizontal=True
            )

            # Denomination selection
            denom_options = {
                f"{currency_data['symbol'] if currency_data else ''}{format_number(item['denomination'], 0)}": item['denomination']
                for item in inventory
            }

            selected_denom = st.selectbox(
                "Select Denomination",
                options=list(denom_options.keys()),
                key="adjustment_denom_select"
            )

            denomination = denom_options[selected_denom]

            col7, col8 = st.columns(2)

            with col7:
                current_qty = next((item['quantity'] for item in inventory if abs(item['denomination'] - denomination) < 0.01), 0)
                st.write(f"**Current Quantity:** {current_qty}")

            with col8:
                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    step=1,
                    key="adjustment_quantity"
                )

            reason = st.text_area(
                "Reason for Adjustment *",
                placeholder="Enter reason for stock adjustment...",
                key="adjustment_reason"
            )

            submitted = st.form_submit_button(
                f"➕ Add Stock" if adjustment_type == "Add Stock" else "➖ Remove Stock",
                use_container_width=True
            )

            if submitted:
                if not reason:
                    show_error_message("Reason is required for stock adjustment")
                    return

                quantity_change = quantity if adjustment_type == "Add Stock" else -quantity

                # Validate adjustment
                is_valid, message = manager.validate_stock_adjustment(
                    currency_code, denomination, quantity_change
                )

                if not is_valid:
                    show_error_message(message)
                    return

                # Process adjustment
                with show_loading_spinner("Processing stock adjustment..."):
                    success = manager.update_inventory(
                        currency_code, denomination, quantity_change, reason
                    )

                    if success:
                        action_type = "added to" if adjustment_type == "Add Stock" else "removed from"
                        show_success_message(
                            f"Successfully {adjustment_type.lower()} {quantity} x {currency_code} {format_number(denomination, 0)} {action_type} inventory"
                        )
                        st.rerun()

def show_stock_adjustment_history():
    """Show stock adjustment history"""
    st.subheader("📜 Stock Adjustment History")

    # This would integrate with audit logs to show inventory adjustments
    # For now, showing a placeholder

    from datetime import timedelta
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    try:
        from database.models import report_model, db
        from utils.auth import get_user_info

        # Get recent inventory-related audit logs
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT al.*, u.full_name as user_name
            FROM audit_logs al
            LEFT JOIN users u ON al.user_id = u.id
            WHERE al.action = 'INVENTORY_ADJUSTMENT'
            AND DATE(al.timestamp) BETWEEN ? AND ?
            ORDER BY al.timestamp DESC
            LIMIT 100
        ''', (start_date, end_date))

        adjustments = [dict(row) for row in cursor.fetchall()]
        conn.close()

        if adjustments:
            # Format for display
            df = pd.DataFrame(adjustments)

            # Parse new_values to extract adjustment details
            def parse_adjustment_details(new_values_str):
                try:
                    import json
                    if new_values_str:
                        data = json.loads(new_values_str)
                        return (data.get('currency_code', 'N/A'),
                               data.get('denomination', 'N/A'),
                               data.get('quantity_change', 0),
                               data.get('reason', 'N/A'))
                    return ('N/A', 'N/A', 0, 'N/A')
                except:
                    return ('N/A', 'N/A', 0, 'N/A')

            df[['currency', 'denomination', 'quantity_change', 'reason']] = df['new_values'].apply(
                lambda x: pd.Series(parse_adjustment_details(x))
            )

            df['adjustment_type'] = df['quantity_change'].apply(
                lambda x: '➕ Stock In' if x > 0 else '➖ Stock Out'
            )

            display_columns = ['timestamp', 'user_name', 'currency', 'denomination',
                              'quantity_change', 'adjustment_type', 'reason']
            df_display = df[display_columns].copy()
            df_display.columns = ['Date & Time', 'User', 'Currency', 'Denomination',
                                 'Quantity Change', 'Type', 'Reason']

            create_data_table(df_display, "Recent Stock Adjustments")
        else:
            show_info_message("No stock adjustments found in the last 30 days")

    except Exception as e:
        show_info_message(f"Unable to load adjustment history: {str(e)}")

def show_inventory_reports():
    """Show inventory reports and analytics"""
    st.subheader("📈 Inventory Reports")

    manager = InventoryManager()

    # Date range for reports
    col1, col2 = st.columns(2)

    with col1:
        report_type = st.selectbox(
            "Report Type",
            options=["Current Inventory Status", "Low Stock Analysis", "Inventory Value Trends"],
            key="inventory_report_type"
        )

    with col2:
        if report_type == "Inventory Value Trends":
            # Date range for trend analysis
            days = st.selectbox(
                "Time Period",
                options=[7, 30, 90, 365],
                format_func=lambda x: f"Last {x} days",
                key="trend_days"
            )

    if report_type == "Current Inventory Status":
        inventory = manager.get_all_inventory()

        if inventory:
            # Create detailed inventory report
            df = pd.DataFrame(inventory)

            # Sort by currency and denomination
            df = df.sort_values(['currency_code', 'denomination'], ascending=[True, False])

            # Status based on quantity
            def get_stock_status(quantity):
                if quantity <= 5:
                    return "🔴 Critical"
                elif quantity <= 10:
                    return "🟡 Low"
                elif quantity <= 50:
                    return "🟢 Normal"
                else:
                    return "🔵 High"

            df['status'] = df['quantity'].apply(get_stock_status)

            # Format for display
            df['formatted_denomination'] = df.apply(
                lambda row: f"{row['currency_code']} {format_number(row['denomination'], 0)}",
                axis=1
            )
            df['formatted_value'] = df.apply(
                lambda row: f"{format_currency(row['denomination'] * row['quantity'], row['currency_code'])}",
                axis=1
            )
            df['idr_value'] = df.apply(
                lambda row: row['denomination'] * row['quantity'] * row.get('buy_rate', 0),
                axis=1
            )
            df['formatted_idr_value'] = df['idr_value'].apply(lambda x: format_currency(x, 'IDR'))

            display_columns = ['currency_code', 'formatted_denomination', 'quantity', 'status',
                              'formatted_value', 'formatted_idr_value', 'last_updated']
            df_display = df[display_columns].copy()
            df_display.columns = ['Currency', 'Denomination', 'Quantity', 'Status',
                                 'Foreign Value', 'IDR Value', 'Last Updated']

            create_data_table(df_display, "Complete Inventory Status")

            # Export options
            col1, col2 = st.columns(2)

            with col1:
                csv_data = df_display.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"inventory_status_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

            with col2:
                show_info_message("Excel export would be implemented here")

    elif report_type == "Low Stock Analysis":
        low_stock_items = manager.get_low_stock_items(threshold=20)

        if low_stock_items:
            df = pd.DataFrame(low_stock_items)

            # Categorize low stock levels
            def categorize_low_stock(quantity):
                if quantity <= 5:
                    return "Critical (≤5)"
                elif quantity <= 10:
                    return "Very Low (6-10)"
                else:
                    return "Low (11-20)"

            df['category'] = df['quantity'].apply(categorize_low_stock)

            # Group by category
            category_summary = df.groupby('category').agg({
                'currency_code': 'count',
                'quantity': 'sum'
            }).rename(columns={'currency_code': 'item_count'})

            # Display category summary
            st.subheader("📊 Low Stock Categories")

            fig = px.bar(
                x=category_summary.index,
                y=category_summary['item_count'],
                title="Low Stock Items by Category",
                labels={'x': 'Category', 'y': 'Number of Items'}
            )
            st.plotly_chart(fig, use_container_width=True)

            # Detailed low stock items
            st.subheader("📋 Detailed Low Stock Items")

            df['formatted_denomination'] = df.apply(
                lambda row: f"{row['currency_code']} {format_number(row['denomination'], 0)}",
                axis=1
            )
            df['urgency'] = df['quantity'].apply(
                lambda x: '🔴 Urgent' if x <= 5 else '🟡 Action Needed'
            )

            display_columns = ['currency_code', 'formatted_denomination', 'quantity', 'category', 'urgency']
            df_display = df[display_columns].copy()
            df_display.columns = ['Currency', 'Denomination', 'Quantity', 'Category', 'Priority']

            create_data_table(df_display, "Items Requiring Restock")

        else:
            show_success_message("All items are well stocked! 🎉")

    elif report_type == "Inventory Value Trends":
        show_info_message("Inventory value trends would be implemented with historical data tracking")

def main():
    """Main function for inventory management module"""
    # Page configuration
    st.set_page_config(
        page_title="Inventory Management - Money Changer",
        page_icon="📦",
        layout="wide"
    )

    # Check authentication and permissions
    if not SessionManager.is_authenticated():
        st.error("Please login to access this page")
        return

    if not RoleManager.has_any_permission(['view_inventory', 'manage_inventory']):
        st.error("You don't have permission to access inventory management")
        return

    # Page header
    st.title("📦 Inventory Management")
    st.markdown("Manage foreign currency stock and denominations")

    # Create tabs
    if RoleManager.has_permission('manage_inventory'):
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Dashboard", "💵 Inventory by Currency", "🔧 Stock Adjustment", "📈 Reports"
        ])

        with tab1:
            show_inventory_dashboard()

        with tab2:
            show_inventory_by_currency()

        with tab3:
            show_stock_adjustment_history()

        with tab4:
            show_inventory_reports()

    else:  # View-only access
        tab1, tab2 = st.tabs(["📊 Dashboard", "💵 Inventory by Currency"])

        with tab1:
            show_inventory_dashboard()

        with tab2:
            show_inventory_by_currency()

if __name__ == "__main__":
    main()