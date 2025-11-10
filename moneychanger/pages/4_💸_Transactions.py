"""
Transactions Page
Streamlit page for transaction processing module
"""

import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the transaction module
from modules.transactions import main

# Page configuration
import streamlit as st
st.set_page_config(
    page_title="Transaction Processing - Money Changer",
    page_icon="💸",
    layout="wide"
)

# Run the transaction module
if __name__ == "__main__":
    main()