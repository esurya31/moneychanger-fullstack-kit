"""
Audit Logs Module for Money Changer Application
Provides comprehensive audit trail and activity tracking
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import plotly.express as px
import plotly.graph_objects as go
import json

# Import database models and utilities
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import report_model, user_model
from utils.auth import SessionManager, RoleManager, require_permission
from utils.helpers import (
    format_currency, format_number, show_success_message, show_error_message,
    show_info_message, create_data_table, create_date_range_selector
)

class AuditManager:
    """Audit logs management class"""

    def __init__(self):
        self.report_model = report_model

    def get_audit_logs(self, start_date: date, end_date: date,
                      user_id: Optional[int] = None,
                      action: Optional[str] = None,
                      table_name: Optional[str] = None) -> List[Dict]:
        """Get audit logs with filters"""
        return self.report_model.get_audit_logs(start_date, end_date, user_id)

    def get_all_users(self) -> List[Dict]:
        """Get all users for filtering"""
        return user_model.get_all_users()

    def get_activity_summary(self, start_date: date, end_date: date) -> Dict:
        """Get activity summary statistics"""
        conn = self.report_model.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                COUNT(*) as total_activities,
                COUNT(DISTINCT user_id) as active_users,
                COUNT(DISTINCT action) as unique_actions,
                COUNT(DISTINCT table_name) as affected_tables,
                COUNT(CASE WHEN action LIKE '%CREATE%' OR action LIKE '%INSERT%' THEN 1 END) as create_actions,
                COUNT(CASE WHEN action LIKE '%UPDATE%' OR action LIKE '%EDIT%' THEN 1 END) as update_actions,
                COUNT(CASE WHEN action LIKE '%DELETE%' THEN 1 END) as delete_actions
            FROM audit_logs
            WHERE DATE(timestamp) BETWEEN ? AND ?
        ''', (start_date, end_date))

        summary = dict(cursor.fetchone())
        conn.close()

        return summary

    def get_action_distribution(self, start_date: date, end_date: date) -> List[Dict]:
        """Get distribution of activities by action type"""
        conn = self.report_model.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                action,
                COUNT(*) as count,
                COUNT(DISTINCT user_id) as unique_users
            FROM audit_logs
            WHERE DATE(timestamp) BETWEEN ? AND ?
            GROUP BY action
            ORDER BY count DESC
        ''', (start_date, end_date))

        distribution = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return distribution

    def get_user_activity(self, start_date: date, end_date: date, limit: int = 20) -> List[Dict]:
        """Get top users by activity count"""
        conn = self.report_model.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                u.full_name,
                u.username,
                u.role,
                COUNT(al.id) as activity_count,
                COUNT(DISTINCT al.action) as unique_actions,
                MAX(al.timestamp) as last_activity
            FROM audit_logs al
            LEFT JOIN users u ON al.user_id = u.id
            WHERE DATE(al.timestamp) BETWEEN ? AND ?
            GROUP BY u.id, u.full_name, u.username, u.role
            HAVING activity_count > 0
            ORDER BY activity_count DESC
            LIMIT ?
        ''', (start_date, end_date, limit))

        user_activity = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return user_activity

    def get_table_activity(self, start_date: date, end_date: date) -> List[Dict]:
        """Get activity by table/affected entity"""
        conn = self.report_model.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                table_name,
                COUNT(*) as activity_count,
                COUNT(DISTINCT user_id) as unique_users,
                COUNT(CASE WHEN action LIKE '%CREATE%' OR action LIKE '%INSERT%' THEN 1 END) as creates,
                COUNT(CASE WHEN action LIKE '%UPDATE%' OR action LIKE '%EDIT%' THEN 1 END) as updates,
                COUNT(CASE WHEN action LIKE '%DELETE%' THEN 1 END) as deletes
            FROM audit_logs
            WHERE DATE(timestamp) BETWEEN ? AND ?
            AND table_name IS NOT NULL
            GROUP BY table_name
            ORDER BY activity_count DESC
        ''', (start_date, end_date))

        table_activity = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return table_activity

    def get_hourly_activity(self, report_date: date) -> List[Dict]:
        """Get hourly activity distribution"""
        conn = self.report_model.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                strftime('%H', timestamp) as hour,
                COUNT(*) as activity_count,
                COUNT(DISTINCT user_id) as unique_users
            FROM audit_logs
            WHERE DATE(timestamp) = ?
            GROUP BY strftime('%H', timestamp)
            ORDER BY hour
        ''', (report_date,))

        hourly_activity = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return hourly_activity

    def search_audit_logs(self, query: str, start_date: date, end_date: date) -> List[Dict]:
        """Search audit logs by text"""
        conn = self.report_model.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT al.*, u.full_name as user_name
            FROM audit_logs al
            LEFT JOIN users u ON al.user_id = u.id
            WHERE DATE(al.timestamp) BETWEEN ? AND ?
            AND (
                al.action LIKE ? OR
                al.table_name LIKE ? OR
                al.new_values LIKE ? OR
                al.old_values LIKE ? OR
                u.full_name LIKE ? OR
                u.username LIKE ?
            )
            ORDER BY al.timestamp DESC
            LIMIT 100
        ''', (start_date, end_date, f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results

def show_audit_dashboard():
    """Show audit logs dashboard with key metrics"""
    st.subheader("📊 Audit Dashboard")

    manager = AuditManager()

    # Default date range (last 7 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=7)

    # Activity summary
    summary = manager.get_activity_summary(start_date, end_date)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Activities", f"{summary['total_activities']:,}")

    with col2:
        st.metric("Active Users", f"{summary['active_users']}")

    with col3:
        st.metric("Unique Actions", f"{summary['unique_actions']}")

    with col4:
        st.metric("Affected Tables", f"{summary['affected_tables']}")

    # Action distribution
    action_dist = manager.get_action_distribution(start_date, end_date)

    if action_dist:
        st.subheader("🎯 Action Distribution")

        action_df = pd.DataFrame(action_dist)

        # Top 10 actions
        top_actions = action_df.head(10)

        fig = px.bar(
            top_actions,
            x='action',
            y='count',
            title='Top 10 Actions by Frequency',
            labels={'action': 'Action Type', 'count': 'Frequency'}
        )
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    # User activity
    user_activity = manager.get_user_activity(start_date, end_date, limit=10)

    if user_activity:
        st.subheader("👥 Most Active Users")

        user_df = pd.DataFrame(user_activity)

        fig = px.bar(
            user_df,
            x='full_name',
            y='activity_count',
            title='Top 10 Users by Activity',
            labels={'full_name': 'User', 'activity_count': 'Activity Count'}
        )
        fig.update_xaxis(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

    # Table activity
    table_activity = manager.get_table_activity(start_date, end_date)

    if table_activity:
        st.subheader("📋 Table Activity")

        table_df = pd.DataFrame(table_activity)

        display_columns = ['table_name', 'activity_count', 'unique_users', 'creates', 'updates', 'deletes']
        table_display = table_df[display_columns].copy()
        table_display.columns = ['Table', 'Activities', 'Users', 'Creates', 'Updates', 'Deletes']

        create_data_table(table_display, "Activity by Table")

def show_audit_logs_list():
    """Show detailed audit logs list with filtering"""
    st.subheader("📜 Audit Logs")

    manager = AuditManager()

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now().date())
    with col3:
        search_query = st.text_input("Search logs...", placeholder="Search actions, users, tables...")

    # Additional filters
    col4, col5, col6 = st.columns(3)

    with col4:
        users = manager.get_all_users()
        user_options = {"All Users": None}
        user_options.update({
            f"{u['full_name']} ({u['username']})": u['id'] for u in users
        })
        selected_user = st.selectbox("Filter by User", options=list(user_options.keys()))

    with col5:
        action_options = ["All Actions", "LOGIN", "LOGOUT", "CREATE_", "UPDATE_", "DELETE_", "PROCESS_"]
        selected_action = st.selectbox("Filter by Action", options=action_options)

    with col6:
        table_options = ["All Tables", "users", "customers", "currencies", "transactions", "denomination_inventory"]
        selected_table = st.selectbox("Filter by Table", options=table_options)

    if start_date > end_date:
        show_error_message("Start date cannot be after end date")
        return

    # Apply filters
    if st.button("🔍 Apply Filters", use_container_width=True):
        with st.spinner("Loading audit logs..."):
            if search_query:
                logs = manager.search_audit_logs(search_query, start_date, end_date)
            else:
                user_id = user_options[selected_user]
                action = selected_action if selected_action != "All Actions" else None
                table_name = selected_table if selected_table != "All Tables" else None

                logs = manager.get_audit_logs(start_date, end_date, user_id)

                # Additional client-side filtering for action and table
                if action:
                    logs = [log for log in logs if action in log.get('action', '')]
                if table_name:
                    logs = [log for log in logs if log.get('table_name') == table_name]

            if logs:
                # Convert to DataFrame
                df = pd.DataFrame(logs)

                # Parse and format data
                def format_json_values(json_str):
                    try:
                        if json_str:
                            data = json.loads(json_str)
                            # Truncate long values
                            formatted = []
                            for key, value in list(data.items())[:3]:  # Show first 3 key-value pairs
                                if len(str(value)) > 50:
                                    formatted.append(f"{key}: {str(value)[:50]}...")
                                else:
                                    formatted.append(f"{key}: {value}")
                            return ", ".join(formatted)
                        return ""
                    except:
                        return str(json_str)[:100] + "..." if json_str and len(json_str) > 100 else (json_str or "")

                df['new_values_formatted'] = df['new_values'].apply(format_json_values)
                df['old_values_formatted'] = df['old_values'].apply(format_json_values)

                # Display metrics
                st.subheader("📊 Filter Results Summary")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total Logs", len(logs))

                with col2:
                    unique_users = len([log['user_id'] for log in logs if log['user_id']])
                    st.metric("Unique Users", unique_users)

                with col3:
                    unique_actions = len(set(log.get('action', '') for log in logs))
                    st.metric("Unique Actions", unique_actions)

                # Display logs table
                st.subheader("📋 Audit Log Details")

                display_columns = ['timestamp', 'user_name', 'action', 'table_name',
                                  'new_values_formatted', 'old_values_formatted']
                df_display = df[display_columns].copy()
                df_display.columns = ['Timestamp', 'User', 'Action', 'Table', 'New Values', 'Old Values']

                create_data_table(df_display, "Filtered Audit Logs")

                # Export options
                col1, col2 = st.columns(2)

                with col1:
                    csv_data = df_display.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name=f"audit_logs_{start_date}_to_{end_date}.csv",
                        mime="text/csv"
                    )

                with col2:
                    show_info_message("Excel export would be implemented here")

            else:
                show_info_message("No audit logs found matching the criteria")

def show_detailed_log_view():
    """Show detailed view for specific log entries"""
    st.subheader("🔍 Detailed Log Analysis")

    manager = AuditManager()

    # Search for specific log entry
    log_id = st.text_input("Enter Log ID for detailed view:", placeholder="Enter numeric ID...")

    if log_id and log_id.isdigit():
        conn = manager.report_model.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT al.*, u.full_name as user_name, u.username
            FROM audit_logs al
            LEFT JOIN users u ON al.user_id = u.id
            WHERE al.id = ?
        ''', (int(log_id),))

        log_entry = cursor.fetchone()
        conn.close()

        if log_entry:
            log_data = dict(log_entry)

            st.markdown("### 📋 Log Entry Details")

            # Basic information
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Log ID:** {log_data['id']}")
                st.write(f"**Timestamp:** {log_data['timestamp']}")
                st.write(f"**User:** {log_data['user_name']} ({log_data['username']})" if log_data['user_name'] else "System")
                st.write(f"**Action:** {log_data['action']}")

            with col2:
                st.write(f"**Table:** {log_data['table_name'] or 'N/A'}")
                st.write(f"**Record ID:** {log_data['record_id'] or 'N/A'}")
                st.write(f"**IP Address:** {log_data['ip_address'] or 'N/A'}")

            # Detailed values
            if log_data.get('old_values'):
                st.subheader("📤 Old Values")
                try:
                    old_data = json.loads(log_data['old_values'])
                    st.json(old_data)
                except:
                    st.code(log_data['old_values'])

            if log_data.get('new_values'):
                st.subheader("📥 New Values")
                try:
                    new_data = json.loads(log_data['new_values'])
                    st.json(new_data)
                except:
                    st.code(log_data['new_values'])

            if log_data.get('user_agent'):
                st.subheader("🌐 User Agent")
                st.code(log_data['user_agent'])

        else:
            show_error_message("Log entry not found")

def show_compliance_reports():
    """Show compliance and security reports"""
    st.subheader("🛡️ Compliance & Security Reports")

    manager = AuditManager()

    # Date range
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=30), key="comp_start")
    with col2:
        end_date = st.date_input("End Date", value=datetime.now().date(), key="comp_end")

    if start_date > end_date:
        show_error_message("Start date cannot be after end date")
        return

    if st.button("🔍 Generate Compliance Report", type="primary", use_container_width=True):
        with st.spinner("Generating compliance report..."):
            # Login/Logout activity
            conn = manager.report_model.db.get_connection()
            cursor = conn.cursor()

            # Get login/logout activities
            cursor.execute('''
                SELECT
                    action,
                    COUNT(*) as count,
                    COUNT(DISTINCT user_id) as unique_users,
                    MIN(timestamp) as first_occurrence,
                    MAX(timestamp) as last_occurrence
                FROM audit_logs
                WHERE DATE(timestamp) BETWEEN ? AND ?
                AND action IN ('LOGIN', 'LOGOUT')
                GROUP BY action
            ''', (start_date, end_date))

            login_activity = [dict(row) for row in cursor.fetchall()]

            # Get data modification activities
            cursor.execute('''
                SELECT
                    u.full_name,
                    u.username,
                    COUNT(*) as modification_count,
                    COUNT(DISTINCT al.table_name) as tables_modified,
                    MAX(al.timestamp) as last_modification
                FROM audit_logs al
                LEFT JOIN users u ON al.user_id = u.id
                WHERE DATE(al.timestamp) BETWEEN ? AND ?
                AND (
                    al.action LIKE '%CREATE%' OR
                    al.action LIKE '%UPDATE%' OR
                    al.action LIKE '%DELETE%' OR
                    al.action LIKE '%INSERT%'
                )
                GROUP BY u.id, u.full_name, u.username
                ORDER BY modification_count DESC
            ''', (start_date, end_date))

            data_modifications = [dict(row) for row in cursor.fetchall()]

            # Get failed login attempts (if tracked)
            cursor.execute('''
                SELECT
                    DATE(timestamp) as date,
                    COUNT(*) as failed_attempts,
                    COUNT(DISTINCT new_values) as unique_usernames
                FROM audit_logs
                WHERE DATE(timestamp) BETWEEN ? AND ?
                AND action = 'FAILED_LOGIN'
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (start_date, end_date))

            failed_logins = [dict(row) for row in cursor.fetchall()]

            conn.close()

            # Display compliance report
            st.markdown("### 🔐 Authentication Activity")

            if login_activity:
                login_df = pd.DataFrame(login_activity)
                create_data_table(login_df, "Login/Logout Activity Summary")

            st.markdown("### 📝 Data Modification Activity")

            if data_modifications:
                mod_df = pd.DataFrame(data_modifications)
                display_columns = ['full_name', 'username', 'modification_count', 'tables_modified', 'last_modification']
                mod_display = mod_df[display_columns].copy()
                mod_display.columns = ['Name', 'Username', 'Modifications', 'Tables Modified', 'Last Activity']

                create_data_table(mod_display, "User Data Modifications")

            st.markdown("### 🚨 Security Incidents")

            if failed_logins:
                failed_df = pd.DataFrame(failed_logins)
                st.warning(f"Found {failed_df['failed_attempts'].sum()} failed login attempts in the selected period")

                fig = px.line(
                    failed_df,
                    x='date',
                    y='failed_attempts',
                    title='Failed Login Attempts Trend'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("✅ No failed login attempts recorded in the selected period")

def main():
    """Main function for audit logs module"""
    # Page configuration
    st.set_page_config(
        page_title="Audit Logs - Money Changer",
        page_icon="🔍",
        layout="wide"
    )

    # Check authentication and permissions
    if not SessionManager.is_authenticated():
        st.error("Please login to access this page")
        return

    if not RoleManager.has_permission('view_audit_logs'):
        st.error("You don't have permission to access audit logs")
        return

    # Page header
    st.title("🔍 Audit Logs")
    st.markdown("Comprehensive audit trail and activity monitoring")

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard", "📜 Audit Logs", "🔍 Detailed View", "🛡️ Compliance Reports"
    ])

    with tab1:
        show_audit_dashboard()

    with tab2:
        show_audit_logs_list()

    with tab3:
        show_detailed_log_view()

    with tab4:
        show_compliance_reports()

if __name__ == "__main__":
    main()