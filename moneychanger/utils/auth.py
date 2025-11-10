"""
Authentication and Session Management for Money Changer Application
Handles user login, logout, session management, and role-based access control
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import hashlib
import secrets

# Session configuration
SESSION_TIMEOUT_HOURS = 8
SESSION_KEY = "moneychanger_session"

class AuthenticationError(Exception):
    """Custom authentication error"""
    pass

class AuthorizationError(Exception):
    """Custom authorization error"""
    pass

class SessionManager:
    """Manages user sessions in Streamlit"""

    @staticmethod
    def init_session_state():
        """Initialize session state variables"""
        if 'user' not in st.session_state:
            st.session_state.user = None
        if 'is_authenticated' not in st.session_state:
            st.session_state.is_authenticated = False
        if 'login_time' not in st.session_state:
            st.session_state.login_time = None

    @staticmethod
    def login_user(user_data: Dict):
        """Login user and set session state"""
        st.session_state.user = user_data
        st.session_state.is_authenticated = True
        st.session_state.login_time = datetime.now()

    @staticmethod
    def logout_user():
        """Logout user and clear session state"""
        st.session_state.user = None
        st.session_state.is_authenticated = False
        st.session_state.login_time = None

    @staticmethod
    def is_session_valid() -> bool:
        """Check if current session is valid"""
        if not st.session_state.is_authenticated or not st.session_state.login_time:
            return False

        # Check session timeout
        session_age = datetime.now() - st.session_state.login_time
        if session_age > timedelta(hours=SESSION_TIMEOUT_HOURS):
            SessionManager.logout_user()
            return False

        return True

    @staticmethod
    def get_current_user() -> Optional[Dict]:
        """Get current authenticated user"""
        if SessionManager.is_session_valid():
            return st.session_state.user
        return None

    @staticmethod
    def get_user_role() -> Optional[str]:
        """Get current user role"""
        user = SessionManager.get_current_user()
        return user['role'] if user else None

class RoleManager:
    """Manages role-based access control"""

    # Define role permissions
    ROLE_PERMISSIONS = {
        'Admin': [
            'view_dashboard',
            'manage_users',
            'manage_currencies',
            'manage_customers',
            'process_transactions',
            'view_inventory',
            'manage_inventory',
            'view_reports',
            'generate_reports',
            'view_audit_logs',
            'manage_settings'
        ],
        'Kasir': [
            'view_dashboard',
            'view_currencies',
            'manage_customers',
            'process_transactions',
            'view_inventory',
            'view_reports',
            'generate_basic_reports'
        ],
        'Auditor': [
            'view_dashboard',
            'view_currencies',
            'view_customers',
            'view_transactions',
            'view_inventory',
            'view_reports',
            'generate_reports',
            'view_audit_logs'
        ]
    }

    @staticmethod
    def has_permission(permission: str) -> bool:
        """Check if current user has specific permission"""
        user_role = SessionManager.get_user_role()
        if not user_role:
            return False

        return permission in RoleManager.ROLE_PERMISSIONS.get(user_role, [])

    @staticmethod
    def has_any_permission(permissions: List[str]) -> bool:
        """Check if current user has any of the specified permissions"""
        return any(RoleManager.has_permission(perm) for perm in permissions)

    @staticmethod
    def has_all_permissions(permissions: List[str]) -> bool:
        """Check if current user has all specified permissions"""
        return all(RoleManager.has_permission(perm) for perm in permissions)

    @staticmethod
    def can_access_module(module_name: str) -> bool:
        """Check if current user can access specific module"""
        module_permissions = {
            'dashboard': 'view_dashboard',
            'users': 'manage_users',
            'currencies': 'manage_currencies',
            'customers': 'manage_customers',
            'transactions': 'process_transactions',
            'inventory': 'manage_inventory',
            'reports': 'view_reports',
            'audit': 'view_audit_logs',
            'settings': 'manage_settings'
        }

        permission = module_permissions.get(module_name)
        if not permission:
            return False

        return RoleManager.has_permission(permission)

class Authentication:
    """Main authentication class"""

    def __init__(self, user_model):
        self.user_model = user_model

    def login(self, username: str, password: str) -> Dict:
        """Authenticate user and return user data"""
        if not username or not password:
            raise AuthenticationError("Username and password are required")

        # Authenticate user
        user = self.user_model.authenticate_user(username, password)
        if not user:
            raise AuthenticationError("Invalid username or password")

        # Login user in session
        SessionManager.login_user(user)

        # Log login attempt (successful)
        try:
            from ..database.models import db
            db.log_audit(
                user_id=user['id'],
                action="LOGIN",
                table_name="users",
                record_id=user['id']
            )
        except Exception:
            pass  # Ignore logging errors

        return user

    def logout(self):
        """Logout current user"""
        user = SessionManager.get_current_user()
        if user:
            # Log logout attempt
            try:
                from ..database.models import db
                db.log_audit(
                    user_id=user['id'],
                    action="LOGOUT",
                    table_name="users",
                    record_id=user['id']
                )
            except Exception:
                pass  # Ignore logging errors

        SessionManager.logout_user()

    def require_auth(self):
        """Require authentication to access current page"""
        if not SessionManager.is_session_valid():
            st.error("Please login to access this page")
            st.stop()

    def require_role(self, required_roles: List[str]):
        """Require specific role(s) to access current page"""
        self.require_auth()

        user_role = SessionManager.get_user_role()
        if user_role not in required_roles:
            st.error(f"Access denied. Required role: {', '.join(required_roles)}")
            st.stop()

    def require_permission(self, permission: str):
        """Require specific permission to access current page"""
        self.require_auth()

        if not RoleManager.has_permission(permission):
            st.error(f"Access denied. Required permission: {permission}")
            st.stop()

class AuthUI:
    """Authentication UI components"""

    @staticmethod
    def show_login_form() -> bool:
        """Show login form and return True if login successful"""
        st.title("🏦 Money Changer Login")

        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submit_button = st.form_submit_button("Login", use_container_width=True)

            if submit_button:
                if not username or not password:
                    st.error("Please enter both username and password")
                    return False

                try:
                    from ..database.models import user_model
                    auth = Authentication(user_model)
                    user = auth.login(username, password)

                    st.success(f"Welcome back, {user['full_name']}!")
                    st.rerun()
                    return True

                except AuthenticationError as e:
                    st.error(str(e))
                    return False
                except Exception as e:
                    st.error("Login failed. Please try again.")
                    return False

        return False

    @staticmethod
    def show_logout_button():
        """Show logout button in sidebar"""
        if SessionManager.is_authenticated():
            user = SessionManager.get_current_user()
            st.sidebar.markdown("---")
            st.sidebar.write(f"👤 **{user['full_name']}**")
            st.sidebar.write(f"🔑 **{user['role']}**")

            if st.sidebar.button("🚪 Logout", use_container_width=True):
                try:
                    from ..database.models import user_model
                    auth = Authentication(user_model)
                    auth.logout()
                    st.success("Logged out successfully!")
                    st.rerun()
                except Exception as e:
                    st.error("Logout failed. Please try again.")

    @staticmethod
    def show_navigation_menu():
        """Show navigation menu based on user role"""
        if not SessionManager.is_authenticated():
            return

        st.sidebar.title("🧭 Navigation")

        # Dashboard (all users)
        if RoleManager.has_permission('view_dashboard'):
            st.sidebar.page_link("app.py", label="📊 Dashboard", icon="📊")

        # Master Data modules
        if RoleManager.has_any_permission(['manage_currencies', 'view_currencies']):
            st.sidebar.markdown("### 📁 Master Data")
            if RoleManager.has_permission('manage_currencies'):
                st.sidebar.page_link("pages/currencies.py", label="💱 Currencies", icon="💱")
            elif RoleManager.has_permission('view_currencies'):
                st.sidebar.page_link("pages/currencies.py", label="💱 View Currencies", icon="💱")

            if RoleManager.has_any_permission(['manage_customers', 'view_customers']):
                st.sidebar.page_link("pages/customers.py", label="👥 Customers", icon="👥")

            if RoleManager.has_permission('manage_users'):
                st.sidebar.page_link("pages/users.py", label="👤 Users", icon="👤")

        # Transaction modules
        if RoleManager.has_permission('process_transactions'):
            st.sidebar.markdown("### 💰 Transactions")
            st.sidebar.page_link("pages/transactions.py", label="💸 New Transaction", icon="💸")
            st.sidebar.page_link("pages/transaction_history.py", label="📜 Transaction History", icon="📜")

        # Inventory modules
        if RoleManager.has_any_permission(['manage_inventory', 'view_inventory']):
            st.sidebar.markdown("### 📦 Inventory")
            st.sidebar.page_link("pages/inventory.py", label="📊 Stock Inventory", icon="📊")

        # Report modules
        if RoleManager.has_any_permission(['view_reports', 'generate_reports']):
            st.sidebar.markdown("### 📈 Reports")
            st.sidebar.page_link("pages/reports.py", label="📊 Reports", icon="📊")
            if RoleManager.has_permission('view_audit_logs'):
                st.sidebar.page_link("pages/audit_logs.py", label="🔍 Audit Logs", icon="🔍")

        # Settings (Admin only)
        if RoleManager.has_permission('manage_settings'):
            st.sidebar.markdown("### ⚙️ Settings")
            st.sidebar.page_link("pages/settings.py", label="⚙️ Settings", icon="⚙️")

# Decorators for authentication
def require_authentication(func):
    """Decorator to require authentication"""
    def wrapper(*args, **kwargs):
        try:
            from ..database.models import user_model
            auth = Authentication(user_model)
            auth.require_auth()
            return func(*args, **kwargs)
        except Exception as e:
            st.error("Authentication required")
            return None
    return wrapper

def require_role(required_roles: List[str]):
    """Decorator to require specific role(s)"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                from ..database.models import user_model
                auth = Authentication(user_model)
                auth.require_role(required_roles)
                return func(*args, **kwargs)
            except Exception as e:
                st.error(f"Access denied. Required role: {', '.join(required_roles)}")
                return None
        return wrapper
    return decorator

def require_permission(permission: str):
    """Decorator to require specific permission"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                from ..database.models import user_model
                auth = Authentication(user_model)
                auth.require_permission(permission)
                return func(*args, **kwargs)
            except Exception as e:
                st.error(f"Access denied. Required permission: {permission}")
                return None
        return wrapper
    return decorator

# Utility functions
def get_user_display_name() -> str:
    """Get current user's display name"""
    user = SessionManager.get_current_user()
    return user['full_name'] if user else "Guest"

def get_user_role_display() -> str:
    """Get current user's role display"""
    user = SessionManager.get_current_user()
    return user['role'] if user else "No Role"

def is_admin() -> bool:
    """Check if current user is admin"""
    return SessionManager.get_user_role() == 'Admin'

def is_cashier() -> bool:
    """Check if current user is cashier"""
    return SessionManager.get_user_role() == 'Kasir'

def is_auditor() -> bool:
    """Check if current user is auditor"""
    return SessionManager.get_user_role() == 'Auditor'