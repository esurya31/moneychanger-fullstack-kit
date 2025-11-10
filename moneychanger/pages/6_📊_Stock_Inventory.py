"""
Inventory Management Page
Streamlit page for inventory management module
"""

import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the inventory module
from modules.inventory import main

# Page configuration
import streamlit as st
st.set_page_config(
    page_title="Inventory Management - Money Changer",
    page_icon="📊",
    layout="wide"
)

# Run the inventory module
if __name__ == "__main__":
    main()