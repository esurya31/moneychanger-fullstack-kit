"""
Users Management Page
Streamlit page for user management module
"""

import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the user module
from modules.users import main

# Page configuration
import streamlit as st
st.set_page_config(
    page_title="User Management - Money Changer",
    page_icon="👤",
    layout="wide"
)

# Run the user module
if __name__ == "__main__":
    main()