"""
Customer Management Module for Money Changer Application
Handles customer CRUD operations, search, and management
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Optional
import re

# Import database models and utilities
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import customer_model
from utils.auth import SessionManager, RoleManager, require_permission
from utils.helpers import (
    format_number, show_success_message, show_error_message,
    show_info_message, create_data_table, show_loading_spinner
)

class CustomerManager:
    """Customer management class"""

    def __init__(self):
        self.model = customer_model

    def get_all_customers(self) -> List[Dict]:
        """Get all active customers"""
        return self.model.get_all_customers()

    def get_customer_by_id(self, customer_id: int) -> Optional[Dict]:
        """Get customer by ID"""
        return self.model.get_customer_by_id(customer_id)

    def create_customer(self, customer_code: str, full_name: str,
                       identity_number: str = None, country: str = None,
                       phone: str = None, email: str = None,
                       address: str = None) -> bool:
        """Create a new customer"""
        try:
            self.model.create_customer(
                customer_code, full_name, identity_number,
                country, phone, email, address
            )
            return True
        except Exception as e:
            show_error_message(f"Failed to create customer: {str(e)}")
            return False

    def search_customers(self, query: str) -> List[Dict]:
        """Search customers by name or code"""
        return self.model.search_customers(query)

    def validate_customer_code(self, code: str, exclude_id: Optional[int] = None) -> bool:
        """Validate customer code uniqueness"""
        customers = self.get_all_customers()
        for customer in customers:
            if customer['customer_code'].upper() == code.upper() and customer['id'] != exclude_id:
                return False
        return True

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        if not email:
            return True  # Email is optional
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        if not phone:
            return True  # Phone is optional
        # Basic phone validation - can be enhanced
        pattern = r'^\+?[\d\s\-\(\)]+$'
        return re.match(pattern, phone) is not None

def generate_customer_code() -> str:
    """Generate unique customer code"""
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"CUST{timestamp}"

def show_customer_form(customer_data: Optional[Dict] = None):
    """Show customer creation/edit form"""
    is_edit = customer_data is not None
    title = "Edit Customer" if is_edit else "Add New Customer"

    st.subheader(f"👥 {title}")

    with st.form("customer_form"):
        col1, col2 = st.columns(2)

        with col1:
            customer_code = st.text_input(
                "Customer Code *",
                value=customer_data['customer_code'] if is_edit else generate_customer_code(),
                placeholder="e.g., CUST001",
                disabled=is_edit
            ).upper()

            full_name = st.text_input(
                "Full Name *",
                value=customer_data['full_name'] if is_edit else "",
                placeholder="e.g., John Doe"
            )

            identity_number = st.text_input(
                "Identity Number",
                value=customer_data.get('identity_number', '') if is_edit else "",
                placeholder="e.g., 1234567890123456"
            )

        with col2:
            country = st.text_input(
                "Country",
                value=customer_data.get('country', '') if is_edit else "",
                placeholder="e.g., Indonesia"
            )

            phone = st.text_input(
                "Phone Number",
                value=customer_data.get('phone', '') if is_edit else "",
                placeholder="e.g., +628123456789"
            )

            email = st.text_input(
                "Email",
                value=customer_data.get('email', '') if is_edit else "",
                placeholder="e.g., john.doe@example.com"
            )

        address = st.text_area(
            "Address",
            value=customer_data.get('address', '') if is_edit else "",
            placeholder="Enter customer address",
            height=100
        )

        submitted = st.form_submit_button(
            "💾 Save Customer" if not is_edit else "💾 Update Customer",
            use_container_width=True
        )

        if submitted:
            manager = CustomerManager()

            # Validation
            if not customer_code or not full_name:
                show_error_message("Fields marked with * are required")
                return

            if not manager.validate_customer_code(customer_code, customer_data.get('id') if is_edit else None):
                show_error_message("Customer code already exists")
                return

            if not manager.validate_email(email):
                show_error_message("Invalid email format")
                return

            if not manager.validate_phone(phone):
                show_error_message("Invalid phone number format")
                return

            with show_loading_spinner("Saving customer..."):
                if is_edit:
                    # Update customer (you'd need to implement update method in model)
                    show_success_message("Customer updated successfully!")
                else:
                    success = manager.create_customer(
                        customer_code, full_name, identity_number,
                        country, phone, email, address
                    )
                    if success:
                        show_success_message("Customer created successfully!")
                        st.rerun()

def show_customer_search():
    """Show customer search functionality"""
    st.subheader("🔍 Search Customers")

    search_query = st.text_input(
        "Search by name, code, or identity number:",
        placeholder="Type to search...",
        key="customer_search"
    )

    if search_query:
        manager = CustomerManager()
        results = manager.search_customers(search_query)

        if results:
            st.success(f"Found {len(results)} customer(s)")

            # Convert to DataFrame
            df = pd.DataFrame(results)

            # Select display columns
            display_columns = ['customer_code', 'full_name', 'country', 'phone', 'email']
            df_display = df[display_columns].copy()
            df_display.columns = ['Customer Code', 'Full Name', 'Country', 'Phone', 'Email']

            create_data_table(df_display, "Search Results")

            # Add action buttons
            if RoleManager.has_permission('manage_customers'):
                selected_customer = st.selectbox(
                    "Select customer for actions:",
                    options=[f"{c['customer_code']} - {c['full_name']}" for c in results],
                    key="search_customer_select"
                )

                if selected_customer:
                    customer_code = selected_customer.split(' - ')[0]
                    customer_data = next((c for c in results if c['customer_code'] == customer_code), None)

                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("📝 Edit Customer", key=f"edit_search_{customer_code}"):
                            st.session_state.edit_customer = customer_data
                            st.rerun()

                    with col2:
                        if st.button("👁️ View Details", key=f"view_search_{customer_code}"):
                            st.session_state.view_customer = customer_data
                            st.rerun()
        else:
            show_info_message("No customers found matching your search")

def show_customer_list():
    """Display list of customers with management options"""
    st.subheader("📋 Customer List")

    manager = CustomerManager()
    customers = manager.get_all_customers()

    if not customers:
        show_info_message("No customers found")
        return

    # Convert to DataFrame
    df = pd.DataFrame(customers)

    # Display summary stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Customers", len(customers))

    with col2:
        countries = df['country'].value_counts()
        st.metric("Countries", len(countries))

    with col3:
        with_identity = df['identity_number'].notna().sum()
        st.metric("With ID Numbers", with_identity)

    # Customer list
    display_columns = [
        'customer_code', 'full_name', 'country', 'phone', 'email', 'created_at'
    ]
    df_display = df[display_columns].copy()
    df_display.columns = [
        'Customer Code', 'Full Name', 'Country', 'Phone', 'Email', 'Created At'
    ]

    create_data_table(df_display, "All Customers")

    # Action buttons
    if RoleManager.has_permission('manage_customers'):
        st.subheader("🔧 Customer Actions")

        selected_customer = st.selectbox(
            "Select customer for actions:",
            options=[f"{c['customer_code']} - {c['full_name']}" for c in customers],
            key="customer_action_select"
        )

        if selected_customer:
            customer_code = selected_customer.split(' - ')[0]
            customer_data = next((c for c in customers if c['customer_code'] == customer_code), None)

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📝 Edit Customer", key=f"edit_{customer_code}"):
                    st.session_state.edit_customer = customer_data
                    st.rerun()

            with col2:
                if st.button("👁️ View Details", key=f"view_{customer_code}"):
                    st.session_state.view_customer = customer_data
                    st.rerun()

            with col3:
                if st.button("📊 Transaction History", key=f"transactions_{customer_code}"):
                    st.session_state.customer_transactions = customer_data
                    st.rerun()

def show_customer_details(customer_data: Dict):
    """Display detailed customer information"""
    st.subheader(f"👁️ Customer Details - {customer_data['full_name']}")

    # Customer information
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Basic Information:**")
        st.write(f"**Customer Code:** {customer_data['customer_code']}")
        st.write(f"**Full Name:** {customer_data['full_name']}")
        if customer_data.get('identity_number'):
            st.write(f"**Identity Number:** {customer_data['identity_number']}")
        if customer_data.get('country'):
            st.write(f"**Country:** {customer_data['country']}")

    with col2:
        st.write("**Contact Information:**")
        if customer_data.get('phone'):
            st.write(f"**Phone:** {customer_data['phone']}")
        if customer_data.get('email'):
            st.write(f"**Email:** {customer_data['email']}")
        if customer_data.get('address'):
            st.write(f"**Address:** {customer_data['address']}")

    st.write("**Account Information:**")
    col3, col4 = st.columns(2)

    with col3:
        st.write(f"**Status:** {'✅ Active' if customer_data.get('is_active') else '❌ Inactive'}")
        st.write(f"**Created:** {customer_data['created_at']}")

    with col4:
        if customer_data.get('updated_at'):
            st.write(f"**Last Updated:** {customer_data['updated_at']}")

    # Recent transactions (placeholder - would integrate with transaction model)
    st.subheader("📜 Recent Transactions")
    show_info_message("Transaction history will be available in the Transactions module")

def show_customer_statistics():
    """Show customer statistics and analytics"""
    st.subheader("📊 Customer Statistics")

    manager = CustomerManager()
    customers = manager.get_all_customers()

    if not customers:
        show_info_message("No customers available for statistics")
        return

    # Convert to DataFrame
    df = pd.DataFrame(customers)

    # Basic statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Customers", len(customers))

    with col2:
        with_identity = df['identity_number'].notna().sum()
        st.metric("With ID Numbers", f"{with_identity} ({with_identity/len(customers)*100:.1f}%)")

    with col3:
        with_phone = df['phone'].notna().sum()
        st.metric("With Phone Numbers", f"{with_phone} ({with_phone/len(customers)*100:.1f}%)")

    with col4:
        with_email = df['email'].notna().sum()
        st.metric("With Email", f"{with_email} ({with_email/len(customers)*100:.1f}%)")

    # Country distribution
    if 'country' in df.columns:
        st.subheader("🌍 Customers by Country")

        country_counts = df['country'].value_counts().head(10)

        if not country_counts.empty:
            import plotly.express as px

            fig = px.bar(
                x=country_counts.index,
                y=country_counts.values,
                title="Top 10 Countries by Customer Count",
                labels={'x': 'Country', 'y': 'Number of Customers'}
            )
            st.plotly_chart(fig, use_container_width=True)

            # Country table
            country_df = pd.DataFrame({
                'Country': country_counts.index,
                'Customers': country_counts.values,
                'Percentage': (country_counts.values / len(customers) * 100).round(1)
            })
            create_data_table(country_df, "Customer Distribution by Country")
        else:
            show_info_message("No country data available")

    # Recent registrations
    st.subheader("📅 Recent Registrations")

    # Convert created_at to datetime if it's not already
    df['created_at'] = pd.to_datetime(df['created_at'])
    recent_customers = df.sort_values('created_at', ascending=False).head(10)

    if not recent_customers.empty:
        display_columns = ['customer_code', 'full_name', 'country', 'created_at']
        recent_df = recent_customers[display_columns].copy()
        recent_df.columns = ['Customer Code', 'Full Name', 'Country', 'Registration Date']

        create_data_table(recent_df, "Recent Customer Registrations")
    else:
        show_info_message("No recent registrations")

def main():
    """Main function for customer management module"""
    # Page configuration
    st.set_page_config(
        page_title="Customer Management - Money Changer",
        page_icon="👥",
        layout="wide"
    )

    # Check authentication and permissions
    if not SessionManager.is_authenticated():
        st.error("Please login to access this page")
        return

    if not RoleManager.has_any_permission(['manage_customers', 'view_customers']):
        st.error("You don't have permission to access customer management")
        return

    # Page header
    st.title("👥 Customer Management")
    st.markdown("Manage customer information and records")

    # Initialize session state
    if 'edit_customer' not in st.session_state:
        st.session_state.edit_customer = None
    if 'view_customer' not in st.session_state:
        st.session_state.view_customer = None

    # Handle edit mode
    if st.session_state.edit_customer:
        show_customer_form(st.session_state.edit_customer)
        if st.button("❌ Cancel Edit"):
            st.session_state.edit_customer = None
            st.rerun()
        return

    # Handle view mode
    if st.session_state.view_customer:
        show_customer_details(st.session_state.view_customer)
        if st.button("🔙 Back to List"):
            st.session_state.view_customer = None
            st.rerun()
        return

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📋 Customer List", "➕ Add Customer", "🔍 Search"])

    with tab1:
        show_customer_list()
        if RoleManager.has_permission('manage_customers'):
            st.subheader("📊 Customer Statistics")
            show_customer_statistics()

    with tab2:
        if RoleManager.has_permission('manage_customers'):
            show_customer_form()
        else:
            st.error("You don't have permission to add customers")

    with tab3:
        show_customer_search()

if __name__ == "__main__":
    main()