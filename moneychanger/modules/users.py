"""
User Management Module for Money Changer Application
Handles user CRUD operations, role management, and authentication
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Optional
import secrets
import hashlib

# Import database models and utilities
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import user_model
from utils.auth import SessionManager, RoleManager
from utils.helpers import (
    format_number, show_success_message, show_error_message,
    show_info_message, create_data_table, show_loading_spinner
)

class UserManager:
    """User management class"""

    def __init__(self):
        self.model = user_model

    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        return self.model.get_all_users()

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        return self.model.get_user_by_id(user_id)

    def create_user(self, username: str, password: str, full_name: str,
                   email: str, role: str) -> bool:
        """Create a new user"""
        try:
            self.model.create_user(username, password, full_name, email, role)
            return True
        except Exception as e:
            show_error_message(f"Failed to create user: {str(e)}")
            return False

    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user data"""
        try:
            return self.model.update_user(user_id, **kwargs)
        except Exception as e:
            show_error_message(f"Failed to update user: {str(e)}")
            return False

    def validate_username(self, username: str, exclude_id: Optional[int] = None) -> bool:
        """Validate username uniqueness"""
        users = self.get_all_users()
        for user in users:
            if user['username'].lower() == username.lower() and user['id'] != exclude_id:
                return False
        return True

    def validate_email(self, email: str, exclude_id: Optional[int] = None) -> bool:
        """Validate email format and uniqueness"""
        if not email:
            return True  # Email is optional

        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False

        users = self.get_all_users()
        for user in users:
            if user['email'] and user['email'].lower() == email.lower() and user['id'] != exclude_id:
                return False

        return True

    def reset_password(self, user_id: int, new_password: str) -> bool:
        """Reset user password"""
        try:
            return self.update_user(user_id, password_hash=self._hash_password(new_password))
        except Exception as e:
            show_error_message(f"Failed to reset password: {str(e)}")
            return False

    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"

def generate_secure_password(length: int = 8) -> str:
    """Generate secure random password"""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for i in range(length))

def show_user_form(user_data: Optional[Dict] = None):
    """Show user creation/edit form"""
    is_edit = user_data is not None
    title = "Edit User" if is_edit else "Add New User"

    st.subheader(f"👤 {title}")

    with st.form("user_form"):
        col1, col2 = st.columns(2)

        with col1:
            username = st.text_input(
                "Username *",
                value=user_data['username'] if is_edit else "",
                placeholder="e.g., john_doe",
                disabled=is_edit
            ).lower()

            full_name = st.text_input(
                "Full Name *",
                value=user_data['full_name'] if is_edit else "",
                placeholder="e.g., John Doe"
            )

            email = st.text_input(
                "Email",
                value=user_data.get('email', '') if is_edit else "",
                placeholder="e.g., john.doe@example.com"
            )

        with col2:
            role = st.selectbox(
                "Role *",
                options=['Admin', 'Kasir', 'Auditor'],
                index=['Admin', 'Kasir', 'Auditor'].index(user_data['role']) if is_edit else 0,
                help="Admin: Full access\nKasir: Transaction access\nAuditor: Read-only access"
            )

            if not is_edit:
                password = st.text_input(
                    "Password *",
                    type="password",
                    placeholder="Enter password",
                    help="Leave blank to auto-generate secure password"
                )

                generate_password = st.checkbox("Generate secure password")
                if generate_password:
                    auto_password = generate_secure_password()
                    st.code(f"Generated password: {auto_password}")
                    password = auto_password

            # Status
            if is_edit:
                is_active = st.checkbox(
                    "Active",
                    value=bool(user_data.get('is_active', True)),
                    help="User can login if active"
                )

        submitted = st.form_submit_button(
            "💾 Save User" if not is_edit else "💾 Update User",
            use_container_width=True
        )

        if submitted:
            manager = UserManager()

            # Validation
            if not username or not full_name:
                show_error_message("Fields marked with * are required")
                return

            if not manager.validate_username(username, user_data.get('id') if is_edit else None):
                show_error_message("Username already exists")
                return

            if not manager.validate_email(email, user_data.get('id') if is_edit else None):
                show_error_message("Invalid email format or email already exists")
                return

            if not is_edit and not password:
                show_error_message("Password is required for new users")
                return

            if not is_edit and len(password) < 6:
                show_error_message("Password must be at least 6 characters long")
                return

            with show_loading_spinner("Saving user..."):
                if is_edit:
                    update_data = {
                        'full_name': full_name,
                        'email': email if email else None,
                        'role': role,
                        'is_active': is_active
                    }

                    success = manager.update_user(user_data['id'], **update_data)
                    if success:
                        show_success_message("User updated successfully!")
                        st.rerun()
                else:
                    success = manager.create_user(username, password, full_name, email, role)
                    if success:
                        show_success_message("User created successfully!")
                        st.rerun()

def show_password_reset_form(user_data: Dict):
    """Show password reset form"""
    st.subheader(f"🔐 Reset Password - {user_data['full_name']}")

    with st.form("password_reset_form"):
        new_password = st.text_input(
            "New Password *",
            type="password",
            placeholder="Enter new password"
        )

        confirm_password = st.text_input(
            "Confirm Password *",
            type="password",
            placeholder="Confirm new password"
        )

        generate_password = st.checkbox("Generate secure password")
        if generate_password:
            auto_password = generate_secure_password()
            st.code(f"Generated password: {auto_password}")
            new_password = auto_password
            confirm_password = auto_password

        submitted = st.form_submit_button("🔄 Reset Password", use_container_width=True)

        if submitted:
            if not new_password:
                show_error_message("Password is required")
                return

            if len(new_password) < 6:
                show_error_message("Password must be at least 6 characters long")
                return

            if new_password != confirm_password:
                show_error_message("Passwords do not match")
                return

            manager = UserManager()

            with show_loading_spinner("Resetting password..."):
                success = manager.reset_password(user_data['id'], new_password)
                if success:
                    show_success_message("Password reset successfully!")
                    st.session_state.reset_password_user = None
                    st.rerun()

def show_user_list():
    """Display list of users with management options"""
    st.subheader("📋 User List")

    manager = UserManager()
    users = manager.get_all_users()

    if not users:
        show_info_message("No users found")
        return

    # Convert to DataFrame
    df = pd.DataFrame(users)

    # Display summary stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Users", len(users))

    with col2:
        active_users = len([u for u in users if u.get('is_active')])
        st.metric("Active Users", f"{active_users} ({active_users/len(users)*100:.1f}%)")

    with col3:
        admin_users = len([u for u in users if u['role'] == 'Admin'])
        st.metric("Admins", admin_users)

    with col4:
        cashier_users = len([u for u in users if u['role'] == 'Kasir'])
        st.metric("Cashiers", cashier_users)

    # User list
    df['status'] = df['is_active'].apply(lambda x: '✅ Active' if x else '❌ Inactive')
    display_columns = ['username', 'full_name', 'email', 'role', 'status', 'created_at']
    df_display = df[display_columns].copy()
    df_display.columns = ['Username', 'Full Name', 'Email', 'Role', 'Status', 'Created At']

    create_data_table(df_display, "All Users")

    # Action buttons
    st.subheader("🔧 User Actions")

    selected_user = st.selectbox(
        "Select user for actions:",
        options=[f"{u['username']} - {u['full_name']} ({u['role']})" for u in users],
        key="user_action_select"
    )

    if selected_user:
        username = selected_user.split(' - ')[0]
        user_data = next((u for u in users if u['username'] == username), None)

        if user_data:
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("📝 Edit User", key=f"edit_{username}"):
                    st.session_state.edit_user = user_data
                    st.rerun()

            with col2:
                if st.button("🔐 Reset Password", key=f"reset_{username}"):
                    st.session_state.reset_password_user = user_data
                    st.rerun()

            with col3:
                if st.button("👁️ View Details", key=f"view_{username}"):
                    st.session_state.view_user = user_data
                    st.rerun()

            with col4:
                # Toggle status
                current_status = "Activate" if not user_data.get('is_active') else "Deactivate"
                status_emoji = "✅" if not user_data.get('is_active') else "❌"
                if st.button(f"{status_emoji} {current_status}", key=f"status_{username}"):
                    new_status = not user_data.get('is_active')
                    manager = UserManager()
                    success = manager.update_user(user_data['id'], is_active=new_status)
                    if success:
                        show_success_message(f"User {current_status.lower()}d successfully!")
                        st.rerun()

def show_user_details(user_data: Dict):
    """Display detailed user information"""
    st.subheader(f"👁️ User Details - {user_data['full_name']}")

    # User information
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Basic Information:**")
        st.write(f"**Username:** {user_data['username']}")
        st.write(f"**Full Name:** {user_data['full_name']}")
        st.write(f"**Role:** {user_data['role']}")
        if user_data.get('email'):
            st.write(f"**Email:** {user_data['email']}")

    with col2:
        st.write("**Account Information:**")
        st.write(f"**Status:** {'✅ Active' if user_data.get('is_active') else '❌ Inactive'}")
        st.write(f"**Created:** {user_data['created_at']}")
        if user_data.get('updated_at'):
            st.write(f"**Last Updated:** {user_data['updated_at']}")

    # Role permissions
    st.write("**Role Permissions:**")
    role_permissions = RoleManager.ROLE_PERMISSIONS.get(user_data['role'], [])
    if role_permissions:
        for permission in role_permissions:
            st.write(f"• {permission.replace('_', ' ').title()}")
    else:
        st.write("No specific permissions")

    # Recent activity (placeholder - would integrate with audit logs)
    st.subheader("📜 Recent Activity")
    show_info_message("User activity history will be available in the Audit Logs module")

def show_user_statistics():
    """Show user statistics and analytics"""
    st.subheader("📊 User Statistics")

    manager = UserManager()
    users = manager.get_all_users()

    if not users:
        show_info_message("No users available for statistics")
        return

    # Convert to DataFrame
    df = pd.DataFrame(users)

    # Role distribution
    st.subheader("👥 User Distribution by Role")

    role_counts = df['role'].value_counts()

    import plotly.express as px

    fig = px.pie(
        values=role_counts.values,
        names=role_counts.index,
        title="User Distribution by Role"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Role table
    role_df = pd.DataFrame({
        'Role': role_counts.index,
        'Users': role_counts.values,
        'Percentage': (role_counts.values / len(users) * 100).round(1)
    })
    create_data_table(role_df, "User Distribution by Role")

    # Registration timeline
    st.subheader("📅 User Registrations Over Time")

    df['created_at'] = pd.to_datetime(df['created_at'])
    df['registration_date'] = df['created_at'].dt.date

    registration_counts = df.groupby('registration_date').size().reset_index(name='count')

    if not registration_counts.empty:
        fig = px.line(
            registration_counts,
            x='registration_date',
            y='count',
            title="User Registration Timeline",
            labels={'registration_date': 'Date', 'count': 'New Users'}
        )
        st.plotly_chart(fig, use_container_width=True)

    # Active vs Inactive
    st.subheader("✅ User Status")

    active_count = len([u for u in users if u.get('is_active')])
    inactive_count = len(users) - active_count

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Active Users", f"{active_count} ({active_count/len(users)*100:.1f}%)")

    with col2:
        st.metric("Inactive Users", f"{inactive_count} ({inactive_count/len(users)*100:.1f}%)")

def main():
    """Main function for user management module"""
    # Page configuration
    st.set_page_config(
        page_title="User Management - Money Changer",
        page_icon="👤",
        layout="wide"
    )

    # Check authentication and permissions
    if not SessionManager.is_authenticated():
        st.error("Please login to access this page")
        return

    if not RoleManager.has_permission('manage_users'):
        st.error("You don't have permission to access user management")
        return

    # Page header
    st.title("👤 User Management")
    st.markdown("Manage user accounts, roles, and permissions")

    # Initialize session state
    if 'edit_user' not in st.session_state:
        st.session_state.edit_user = None
    if 'view_user' not in st.session_state:
        st.session_state.view_user = None
    if 'reset_password_user' not in st.session_state:
        st.session_state.reset_password_user = None

    # Handle edit mode
    if st.session_state.edit_user:
        show_user_form(st.session_state.edit_user)
        if st.button("❌ Cancel Edit"):
            st.session_state.edit_user = None
            st.rerun()
        return

    # Handle view mode
    if st.session_state.view_user:
        show_user_details(st.session_state.view_user)
        if st.button("🔙 Back to List"):
            st.session_state.view_user = None
            st.rerun()
        return

    # Handle password reset
    if st.session_state.reset_password_user:
        show_password_reset_form(st.session_state.reset_password_user)
        if st.button("❌ Cancel Reset"):
            st.session_state.reset_password_user = None
            st.rerun()
        return

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📋 User List", "➕ Add User", "📊 Statistics"])

    with tab1:
        show_user_list()

    with tab2:
        show_user_form()

    with tab3:
        show_user_statistics()

if __name__ == "__main__":
    main()