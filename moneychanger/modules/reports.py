"""
Comprehensive Reporting System for Money Changer Application
Handles financial reports, transaction analytics, and business insights
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# Import database models and utilities
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import report_model, currency_model, customer_model, transaction_model
from utils.auth import SessionManager, RoleManager, require_permission
from utils.helpers import (
    format_currency, format_number, show_success_message, show_error_message,
    show_info_message, create_data_table, create_date_range_selector,
    create_transaction_chart, export_to_csv
)

class ReportManager:
    """Report management class"""

    def __init__(self):
        self.report_model = report_model
        self.currency_model = currency_model
        self.customer_model = customer_model

    def get_daily_summary(self, report_date: date) -> Dict:
        """Get daily transaction summary"""
        return self.report_model.get_daily_summary(report_date)

    def get_profit_loss_report(self, start_date: date, end_date: date) -> List[Dict]:
        """Get profit/loss report by currency"""
        return self.report_model.get_profit_loss_report(start_date, end_date)

    def get_transaction_summary(self, start_date: date, end_date: date,
                              currency_code: Optional[str] = None,
                              customer_id: Optional[int] = None) -> Dict:
        """Get comprehensive transaction summary"""
        conn = self.report_model.db.get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT
                COUNT(*) as total_transactions,
                COUNT(CASE WHEN transaction_type = 'BUY' THEN 1 END) as buy_transactions,
                COUNT(CASE WHEN transaction_type = 'SELL' THEN 1 END) as sell_transactions,
                SUM(CASE WHEN transaction_type = 'BUY' THEN idr_amount ELSE 0 END) as total_buy_idr,
                SUM(CASE WHEN transaction_type = 'SELL' THEN idr_amount ELSE 0 END) as total_sell_idr,
                SUM(foreign_amount) as total_foreign_amount,
                AVG(foreign_amount) as avg_transaction_amount,
                MAX(foreign_amount) as max_transaction_amount,
                MIN(foreign_amount) as min_transaction_amount
            FROM transactions
            WHERE DATE(transaction_date) BETWEEN ? AND ? AND status = 'COMPLETED'
        '''
        params = [start_date, end_date]

        if currency_code:
            query += ' AND currency_code = ?'
            params.append(currency_code)

        if customer_id:
            query += ' AND customer_id = ?'
            params.append(customer_id)

        cursor.execute(query, params)
        summary = dict(cursor.fetchone())
        conn.close()

        return summary

    def get_currency_performance(self, start_date: date, end_date: date) -> List[Dict]:
        """Get performance metrics by currency"""
        conn = self.report_model.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                t.currency_code,
                c.name as currency_name,
                c.symbol,
                COUNT(*) as transaction_count,
                SUM(t.foreign_amount) as total_foreign_amount,
                SUM(t.idr_amount) as total_idr_amount,
                AVG(t.foreign_amount) as avg_foreign_amount,
                COUNT(CASE WHEN t.transaction_type = 'BUY' THEN 1 END) as buy_count,
                COUNT(CASE WHEN t.transaction_type = 'SELL' THEN 1 END) as sell_count,
                (SUM(CASE WHEN t.transaction_type = 'SELL' THEN t.foreign_amount ELSE 0 END) * c.sell_rate) -
                (SUM(CASE WHEN t.transaction_type = 'BUY' THEN t.foreign_amount ELSE 0 END) * c.buy_rate) as gross_profit
            FROM transactions t
            JOIN currencies c ON t.currency_code = c.code
            WHERE DATE(t.transaction_date) BETWEEN ? AND ? AND t.status = 'COMPLETED'
            GROUP BY t.currency_code, c.name, c.symbol, c.buy_rate, c.sell_rate
            ORDER BY total_idr_amount DESC
        ''', (start_date, end_date))

        performance = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return performance

    def get_customer_analytics(self, start_date: date, end_date: date, limit: int = 20) -> List[Dict]:
        """Get top customers by transaction volume"""
        conn = self.report_model.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                c.customer_code,
                c.full_name,
                c.country,
                COUNT(t.id) as transaction_count,
                SUM(t.idr_amount) as total_idr_amount,
                SUM(t.foreign_amount) as total_foreign_amount,
                AVG(t.idr_amount) as avg_transaction_value,
                MAX(t.transaction_date) as last_transaction_date
            FROM customers c
            JOIN transactions t ON c.id = t.customer_id
            WHERE DATE(t.transaction_date) BETWEEN ? AND ? AND t.status = 'COMPLETED'
            GROUP BY c.id, c.customer_code, c.full_name, c.country
            ORDER BY total_idr_amount DESC
            LIMIT ?
        ''', (start_date, end_date, limit))

        analytics = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return analytics

    def get_daily_trends(self, start_date: date, end_date: date) -> List[Dict]:
        """Get daily transaction trends"""
        conn = self.report_model.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                DATE(transaction_date) as date,
                COUNT(*) as transaction_count,
                SUM(idr_amount) as total_revenue,
                SUM(foreign_amount) as total_foreign_amount,
                COUNT(CASE WHEN transaction_type = 'BUY' THEN 1 END) as buy_count,
                COUNT(CASE WHEN transaction_type = 'SELL' THEN 1 END) as sell_count
            FROM transactions
            WHERE DATE(transaction_date) BETWEEN ? AND ? AND status = 'COMPLETED'
            GROUP BY DATE(transaction_date)
            ORDER BY date
        ''', (start_date, end_date))

        trends = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return trends

    def get_hourly_distribution(self, report_date: date) -> List[Dict]:
        """Get hourly transaction distribution"""
        conn = self.report_model.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                strftime('%H', transaction_date) as hour,
                COUNT(*) as transaction_count,
                SUM(idr_amount) as total_revenue
            FROM transactions
            WHERE DATE(transaction_date) = ? AND status = 'COMPLETED'
            GROUP BY strftime('%H', transaction_date)
            ORDER BY hour
        ''', (report_date,))

        distribution = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return distribution

def show_executive_dashboard():
    """Show executive dashboard with key metrics"""
    st.subheader("🏢 Executive Dashboard")

    manager = ReportManager()

    # Default date range (last 30 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    # Key metrics
    summary = manager.get_transaction_summary(start_date, end_date)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Transactions", f"{summary['total_transactions']:,}")

    with col2:
        st.metric("Total Revenue", format_currency(summary.get('total_sell_idr', 0), 'IDR'))

    with col3:
        net_revenue = summary.get('total_sell_idr', 0) - summary.get('total_buy_idr', 0)
        delta_color = "normal" if net_revenue >= 0 else "inverse"
        st.metric("Net Revenue", format_currency(net_revenue, 'IDR'), delta_color=delta_color)

    with col4:
        avg_transaction = summary.get('avg_transaction_amount', 0)
        st.metric("Avg Transaction", format_number(avg_transaction, 2))

    # Currency performance
    currency_performance = manager.get_currency_performance(start_date, end_date)

    if currency_performance:
        st.subheader("💱 Currency Performance")

        # Create currency performance chart
        perf_df = pd.DataFrame(currency_performance)

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Transaction Count', 'Revenue (IDR)', 'Average Transaction Size', 'Gross Profit'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        # Transaction count
        fig.add_trace(
            go.Bar(x=perf_df['currency_code'], y=perf_df['transaction_count'], name="Transactions"),
            row=1, col=1
        )

        # Revenue
        fig.add_trace(
            go.Bar(x=perf_df['currency_code'], y=perf_df['total_idr_amount'], name="Revenue (IDR)"),
            row=1, col=2
        )

        # Average transaction
        fig.add_trace(
            go.Bar(x=perf_df['currency_code'], y=perf_df['avg_foreign_amount'], name="Avg Size"),
            row=2, col=1
        )

        # Gross profit
        fig.add_trace(
            go.Bar(x=perf_df['currency_code'], y=perf_df['gross_profit'], name="Profit"),
            row=2, col=2
        )

        fig.update_layout(height=600, showlegend=False, title_text="Currency Performance Overview")
        st.plotly_chart(fig, use_container_width=True)

    # Daily trends
    trends = manager.get_daily_trends(start_date, end_date)

    if trends:
        st.subheader("📈 Daily Transaction Trends")

        trends_df = pd.DataFrame(trends)

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Transaction Count', 'Revenue (IDR)'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )

        fig.add_trace(
            go.Scatter(x=trends_df['date'], y=trends_df['transaction_count'], mode='lines+markers', name="Count"),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(x=trends_df['date'], y=trends_df['total_revenue'], mode='lines+markers', name="Revenue"),
            row=1, col=2
        )

        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

def show_financial_reports():
    """Show financial reports including P&L"""
    st.subheader("💰 Financial Reports")

    # Date range selection
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now().date())

    if start_date > end_date:
        show_error_message("Start date cannot be after end date")
        return

    manager = ReportManager()

    # Generate P&L Report
    st.subheader("📊 Profit & Loss Report")

    profit_loss = manager.get_profit_loss_report(start_date, end_date)

    if profit_loss:
        pl_df = pd.DataFrame(profit_loss)

        # Calculate additional metrics
        pl_df['profit_margin'] = (pl_df['gross_profit'] / (pl_df['total_sell'] + pl_df['total_buy']) * 100)

        # P&L Summary
        total_buy = pl_df['total_buy'].sum()
        total_sell = pl_df['total_sell'].sum()
        gross_profit = pl_df['gross_profit'].sum()
        profit_margin = (gross_profit / (total_sell + total_buy) * 100) if (total_sell + total_buy) > 0 else 0

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Buy Volume", format_currency(total_buy, 'IDR'))

        with col2:
            st.metric("Total Sell Volume", format_currency(total_sell, 'IDR'))

        with col3:
            st.metric("Gross Profit", format_currency(gross_profit, 'IDR'))

        with col4:
            st.metric("Profit Margin", f"{profit_margin:.2f}%")

        # P&L Details Table
        pl_df['buy_formatted'] = pl_df['total_buy'].apply(lambda x: format_currency(x, 'IDR'))
        pl_df['sell_formatted'] = pl_df['total_sell'].apply(lambda x: format_currency(x, 'IDR'))
        pl_df['profit_formatted'] = pl_df['gross_profit'].apply(lambda x: format_currency(x, 'IDR'))

        display_columns = ['currency_name', 'total_buy', 'total_sell', 'gross_profit', 'profit_margin']
        pl_display = pl_df[display_columns].copy()
        pl_display.columns = ['Currency', 'Buy Volume', 'Sell Volume', 'Gross Profit', 'Margin %']

        create_data_table(pl_display, "Profit & Loss by Currency")

        # P&L Chart
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=pl_df['currency_code'],
            y=pl_df['total_buy'],
            name='Buy Volume',
            marker_color='red'
        ))

        fig.add_trace(go.Bar(
            x=pl_df['currency_code'],
            y=pl_df['total_sell'],
            name='Sell Volume',
            marker_color='green'
        ))

        fig.update_layout(
            title='Buy vs Sell Volume by Currency',
            xaxis_title='Currency',
            yaxis_title='Amount (IDR)',
            barmode='group'
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        show_info_message("No transaction data found for the selected period")

def show_transaction_analytics():
    """Show detailed transaction analytics"""
    st.subheader("📊 Transaction Analytics")

    # Date range selection
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=30), key="txn_start")
    with col2:
        end_date = st.date_input("End Date", value=datetime.now().date(), key="txn_end")

    if start_date > end_date:
        show_error_message("Start date cannot be after end date")
        return

    manager = ReportManager()

    # Transaction Summary
    summary = manager.get_transaction_summary(start_date, end_date)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Transactions", f"{summary['total_transactions']:,}")

    with col2:
        st.metric("Buy Transactions", f"{summary['buy_transactions']:,}")

    with col3:
        st.metric("Sell Transactions", f"{summary['sell_transactions']:,}")

    with col4:
        buy_total = summary.get('total_buy_idr', 0)
        sell_total = summary.get('total_sell_idr', 0)
        st.metric("Total Volume", format_currency(buy_total + sell_total, 'IDR'))

    # Transaction Trends
    trends = manager.get_daily_trends(start_date, end_date)

    if trends:
        st.subheader("📈 Transaction Trends")

        trends_df = pd.DataFrame(trends)

        # Multi-axis chart
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Daily Transaction Count', 'Daily Revenue (IDR)'),
            vertical_spacing=0.1
        )

        fig.add_trace(
            go.Scatter(x=trends_df['date'], y=trends_df['transaction_count'],
                      mode='lines+markers', name='Transactions', line=dict(color='blue')),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(x=trends_df['date'], y=trends_df['total_revenue'],
                      mode='lines+markers', name='Revenue', line=dict(color='green')),
            row=2, col=1
        )

        fig.update_layout(height=600, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Hourly Distribution (for today)
    if end_date == datetime.now().date():
        st.subheader("⏰ Today's Hourly Distribution")

        hourly = manager.get_hourly_distribution(end_date)

        if hourly:
            hourly_df = pd.DataFrame(hourly)

            fig = px.bar(
                hourly_df,
                x='hour',
                y='transaction_count',
                title='Transactions by Hour of Day',
                labels={'hour': 'Hour', 'transaction_count': 'Number of Transactions'}
            )
            st.plotly_chart(fig, use_container_width=True)

def show_customer_analytics():
    """Show customer analytics and insights"""
    st.subheader("👥 Customer Analytics")

    # Date range selection
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=30), key="cust_start")
    with col2:
        end_date = st.date_input("End Date", value=datetime.now().date(), key="cust_end")

    if start_date > end_date:
        show_error_message("Start date cannot be after end date")
        return

    manager = ReportManager()

    # Top Customers
    st.subheader("🏆 Top Customers by Volume")

    top_customers = manager.get_customer_analytics(start_date, end_date, limit=10)

    if top_customers:
        customers_df = pd.DataFrame(top_customers)

        # Customer performance chart
        fig = px.bar(
            customers_df.head(5),
            x='full_name',
            y='total_idr_amount',
            title='Top 5 Customers by Transaction Volume',
            labels={'full_name': 'Customer', 'total_idr_amount': 'Total IDR Volume'}
        )
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

        # Customer details table
        customers_df['total_idr_formatted'] = customers_df['total_idr_amount'].apply(
            lambda x: format_currency(x, 'IDR')
        )
        customers_df['avg_formatted'] = customers_df['avg_transaction_value'].apply(
            lambda x: format_currency(x, 'IDR')
        )

        display_columns = ['customer_code', 'full_name', 'country', 'transaction_count',
                          'total_idr_formatted', 'avg_formatted']
        customer_display = customers_df[display_columns].copy()
        customer_display.columns = ['Code', 'Name', 'Country', 'Transactions', 'Total Volume', 'Avg Transaction']

        create_data_table(customer_display, "Top Customers Details")

        # Geographic distribution
        if 'country' in customers_df.columns:
            st.subheader("🌍 Geographic Distribution")

            country_counts = customers_df['country'].value_counts()

            if not country_counts.empty:
                fig = px.pie(
                    values=country_counts.values,
                    names=country_counts.index,
                    title="Customers by Country"
                )
                st.plotly_chart(fig, use_container_width=True)

    else:
        show_info_message("No customer data found for the selected period")

def show_custom_reports():
    """Show custom report builder"""
    st.subheader("🔧 Custom Report Builder")

    # Report configuration
    col1, col2 = st.columns(2)

    with col1:
        report_type = st.selectbox(
            "Report Type",
            options=["Transaction Summary", "Customer Analysis", "Currency Performance", "Profit & Loss"],
            key="custom_report_type"
        )

        start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=30), key="custom_start")
        end_date = st.date_input("End Date", value=datetime.now().date(), key="custom_end")

    with col2:
        # Additional filters based on report type
        if report_type in ["Transaction Summary", "Customer Analysis"]:
            include_charts = st.checkbox("Include Charts", value=True)
            include_details = st.checkbox("Include Detailed Breakdown", value=True)

        elif report_type == "Currency Performance":
            include_profit_analysis = st.checkbox("Include Profit Analysis", value=True)
            include_trends = st.checkbox("Include Trend Analysis", value=True)

        elif report_type == "Profit & Loss":
            include_margins = st.checkbox("Include Profit Margins", value=True)
            compare_periods = st.checkbox("Compare with Previous Period", value=False)

    if start_date > end_date:
        show_error_message("Start date cannot be after end date")
        return

    # Generate report button
    if st.button("🚀 Generate Custom Report", type="primary", use_container_width=True):
        with st.spinner("Generating custom report..."):
            manager = ReportManager()

            if report_type == "Transaction Summary":
                summary = manager.get_transaction_summary(start_date, end_date)
                display_transaction_summary(summary, start_date, end_date, include_charts, include_details)

            elif report_type == "Customer Analysis":
                customers = manager.get_customer_analytics(start_date, end_date, limit=50)
                display_customer_analysis(customers, include_charts, include_details)

            elif report_type == "Currency Performance":
                performance = manager.get_currency_performance(start_date, end_date)
                display_currency_performance(performance, include_profit_analysis, include_trends)

            elif report_type == "Profit & Loss":
                profit_loss = manager.get_profit_loss_report(start_date, end_date)
                display_profit_loss(profit_loss, start_date, end_date, include_margins, compare_periods)

def display_transaction_summary(summary: Dict, start_date: date, end_date: date,
                               include_charts: bool, include_details: bool):
    """Display transaction summary report"""
    st.markdown(f"### 📊 Transaction Summary Report")
    st.markdown(f"**Period:** {start_date} to {end_date}")

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Transactions", f"{summary['total_transactions']:,}")

    with col2:
        st.metric("Buy Transactions", f"{summary['buy_transactions']:,}")

    with col3:
        st.metric("Sell Transactions", f"{summary['sell_transactions']:,}")

    with col4:
        avg_amount = summary.get('avg_transaction_amount', 0)
        st.metric("Average Amount", format_number(avg_amount, 2))

    if include_details:
        st.subheader("📋 Detailed Breakdown")

        details_df = pd.DataFrame([{
            'Metric': 'Total Transactions',
            'Value': f"{summary['total_transactions']:,}",
            'Percentage': '100%'
        }, {
            'Metric': 'Buy Transactions',
            'Value': f"{summary['buy_transactions']:,}",
            'Percentage': f"{(summary['buy_transactions']/summary['total_transactions']*100):.1f}%"
        }, {
            'Metric': 'Sell Transactions',
            'Value': f"{summary['sell_transactions']:,}",
            'Percentage': f"{(summary['sell_transactions']/summary['total_transactions']*100):.1f}%"
        }])

        create_data_table(details_df, "Transaction Breakdown")

def display_customer_analysis(customers: List[Dict], include_charts: bool, include_details: bool):
    """Display customer analysis report"""
    st.markdown("### 👥 Customer Analysis Report")

    if not customers:
        show_info_message("No customer data available")
        return

    customers_df = pd.DataFrame(customers)

    if include_charts:
        # Top customers chart
        fig = px.bar(
            customers_df.head(10),
            x='full_name',
            y='total_idr_amount',
            title='Top 10 Customers by Transaction Volume'
        )
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    if include_details:
        customers_df['total_idr_formatted'] = customers_df['total_idr_amount'].apply(
            lambda x: format_currency(x, 'IDR')
        )
        customers_df['avg_formatted'] = customers_df['avg_transaction_value'].apply(
            lambda x: format_currency(x, 'IDR')
        )

        display_columns = ['customer_code', 'full_name', 'country', 'transaction_count',
                          'total_idr_formatted', 'avg_formatted', 'last_transaction_date']
        customer_display = customers_df[display_columns].copy()
        customer_display.columns = ['Code', 'Name', 'Country', 'Transactions', 'Total Volume', 'Avg Transaction', 'Last Transaction']

        create_data_table(customer_display, "Customer Analysis Details")

def display_currency_performance(performance: List[Dict], include_profit_analysis: bool, include_trends: bool):
    """Display currency performance report"""
    st.markdown("### 💱 Currency Performance Report")

    if not performance:
        show_info_message("No currency performance data available")
        return

    perf_df = pd.DataFrame(performance)

    if include_charts:
        # Revenue by currency
        fig = px.bar(
            perf_df,
            x='currency_code',
            y='total_idr_amount',
            title='Revenue by Currency'
        )
        st.plotly_chart(fig, use_container_width=True)

    perf_df['total_idr_formatted'] = perf_df['total_idr_amount'].apply(
        lambda x: format_currency(x, 'IDR')
    )
    perf_df['avg_formatted'] = perf_df['avg_foreign_amount'].apply(
        lambda x: format_number(x, 2)
    )

    display_columns = ['currency_code', 'currency_name', 'transaction_count',
                      'total_idr_formatted', 'avg_formatted']
    perf_display = perf_df[display_columns].copy()
    perf_display.columns = ['Code', 'Name', 'Transactions', 'Total Revenue', 'Average Size']

    create_data_table(perf_display, "Currency Performance Details")

def display_profit_loss(profit_loss: List[Dict], start_date: date, end_date: date,
                       include_margins: bool, compare_periods: bool):
    """Display profit & loss report"""
    st.markdown("### 💰 Profit & Loss Report")
    st.markdown(f"**Period:** {start_date} to {end_date}")

    if not profit_loss:
        show_info_message("No profit & loss data available")
        return

    pl_df = pd.DataFrame(profit_loss)

    if include_margins:
        pl_df['profit_margin'] = (pl_df['gross_profit'] / (pl_df['total_sell'] + pl_df['total_buy']) * 100)

    # Summary metrics
    total_profit = pl_df['gross_profit'].sum()
    avg_margin = pl_df['profit_margin'].mean() if include_margins else 0

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Total Gross Profit", format_currency(total_profit, 'IDR'))

    with col2:
        if include_margins:
            st.metric("Average Margin", f"{avg_margin:.2f}%")

    pl_df['profit_formatted'] = pl_df['gross_profit'].apply(lambda x: format_currency(x, 'IDR'))

    display_columns = ['currency_name', 'total_buy', 'total_sell', 'profit_formatted']
    if include_margins:
        display_columns.append('profit_margin')

    pl_display = pl_df[display_columns].copy()
    pl_display.columns = ['Currency', 'Buy Volume', 'Sell Volume', 'Gross Profit']
    if include_margins:
        pl_display.columns = ['Currency', 'Buy Volume', 'Sell Volume', 'Gross Profit', 'Margin %']

    create_data_table(pl_display, "Profit & Loss by Currency")

def main():
    """Main function for reports module"""
    # Page configuration
    st.set_page_config(
        page_title="Reports - Money Changer",
        page_icon="📊",
        layout="wide"
    )

    # Check authentication and permissions
    if not SessionManager.is_authenticated():
        st.error("Please login to access this page")
        return

    if not RoleManager.has_any_permission(['view_reports', 'generate_reports']):
        st.error("You don't have permission to access reports")
        return

    # Page header
    st.title("📊 Business Reports")
    st.markdown("Generate comprehensive business reports and analytics")

    # Create tabs based on permissions
    if RoleManager.has_permission('generate_reports'):
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🏢 Executive Dashboard", "💰 Financial Reports", "📊 Transaction Analytics",
            "👥 Customer Analytics", "🔧 Custom Reports"
        ])

        with tab1:
            show_executive_dashboard()

        with tab2:
            show_financial_reports()

        with tab3:
            show_transaction_analytics()

        with tab4:
            show_customer_analytics()

        with tab5:
            show_custom_reports()

    else:  # View-only access
        tab1, tab2, tab3 = st.tabs([
            "🏢 Executive Dashboard", "💰 Financial Reports", "📊 Transaction Analytics"
        ])

        with tab1:
            show_executive_dashboard()

        with tab2:
            show_financial_reports()

        with tab3:
            show_transaction_analytics()

if __name__ == "__main__":
    main()