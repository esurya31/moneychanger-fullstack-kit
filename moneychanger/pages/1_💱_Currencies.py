"""
Currencies Management Page
Streamlit page for currency management module
"""

import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the currency module
from modules.currencies import main

# Page configuration
import streamlit as st
st.set_page_config(
    page_title="Currency Management - Money Changer",
    page_icon="💱",
    layout="wide"
)

# Run the currency module
if __name__ == "__main__":
    main()