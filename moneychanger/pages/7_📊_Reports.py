"""
Reports Page
Streamlit page for comprehensive reporting system
"""

import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the reports module
from modules.reports import main

# Page configuration
import streamlit as st
st.set_page_config(
    page_title="Business Reports - Money Changer",
    page_icon="📊",
    layout="wide"
)

# Run the reports module
if __name__ == "__main__":
    main()