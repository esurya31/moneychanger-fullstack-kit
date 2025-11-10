"""
Audit Logs Page
Streamlit page for audit trail and activity monitoring
"""

import sys
import os

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the audit logs module
from modules.audit_logs import main

# Page configuration
import streamlit as st
st.set_page_config(
    page_title="Audit Logs - Money Changer",
    page_icon="🔍",
    layout="wide"
)

# Run the audit logs module
if __name__ == "__main__":
    main()