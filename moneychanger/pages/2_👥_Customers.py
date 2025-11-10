"""
Customers Management Page
Streamlit page for customer management module
"""

import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the customer module
from modules.customers import main

# Page configuration
import streamlit as st
st.set_page_config(
    page_title="Customer Management - Money Changer",
    page_icon="👥",
    layout="wide"
)

# Run the customer module
if __name__ == "__main__":
    main()