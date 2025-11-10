"""
Transaction History Page
Streamlit page for viewing transaction history
"""

import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the transaction module (it has history functionality)
from modules.transactions import main

# Page configuration
import streamlit as st
st.set_page_config(
    page_title="Transaction History - Money Changer",
    page_icon="📜",
    layout="wide"
)

# Auto-switch to history tab
if 'auto_history_tab' not in st.session_state:
    st.session_state.auto_history_tab = True

# Run the transaction module
if __name__ == "__main__":
    main()