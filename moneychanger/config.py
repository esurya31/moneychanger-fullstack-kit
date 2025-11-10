"""
Configuration settings for Money Changer Application
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database settings
DATABASE_PATH = BASE_DIR / "data" / "moneychanger.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Ensure data directory exists
os.makedirs(DATABASE_PATH.parent, exist_ok=True)

# Application settings
APP_NAME = "Money Changer System"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Complete Foreign Exchange Management System"

# Security settings
SESSION_TIMEOUT_HOURS = 8
PASSWORD_MIN_LENGTH = 6
MAX_LOGIN_ATTEMPTS = 5

# Currency settings
DEFAULT_CURRENCIES = [
    {"code": "USD", "name": "United States Dollar", "symbol": "$"},
    {"code": "EUR", "name": "Euro", "symbol": "€"},
    {"code": "GBP", "name": "British Pound Sterling", "symbol": "£"},
    {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
    {"code": "SGD", "name": "Singapore Dollar", "symbol": "S$"},
    {"code": "AUD", "name": "Australian Dollar", "symbol": "A$"},
    {"code": "MYR", "name": "Malaysian Ringgit", "symbol": "RM"},
    {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥"},
    {"code": "SAR", "name": "Saudi Riyal", "symbol": "﷼"},
    {"code": "THB", "name": "Thai Baht", "symbol": "฿"}
]

# User roles and permissions
USER_ROLES = {
    "Admin": {
        "description": "Full system access",
        "permissions": [
            "view_dashboard", "manage_users", "manage_currencies",
            "manage_customers", "process_transactions", "view_inventory",
            "manage_inventory", "view_reports", "generate_reports",
            "view_audit_logs", "manage_settings"
        ]
    },
    "Kasir": {
        "description": "Transaction processing and basic reports",
        "permissions": [
            "view_dashboard", "view_currencies", "manage_customers",
            "process_transactions", "view_inventory", "view_reports",
            "generate_basic_reports"
        ]
    },
    "Auditor": {
        "description": "Read-only access for auditing",
        "permissions": [
            "view_dashboard", "view_currencies", "view_customers",
            "view_transactions", "view_inventory", "view_reports",
            "generate_reports", "view_audit_logs"
        ]
    }
}

# Business settings
LOW_STOCK_THRESHOLD = 10
CRITICAL_STOCK_THRESHOLD = 5
MAX_TRANSACTION_AMOUNT = 100000000  # 100M IDR
TRANSACTION_RECEIPT_PREFIX = "TRX"

# UI/UX Settings
PAGE_TITLE_TEMPLATE = "{} - Money Changer"
DEFAULT_PAGE_LAYOUT = "wide"
PAGE_ICON = "🏦"

# Export settings
EXPORT_FORMATS = ["CSV", "Excel", "PDF"]
MAX_EXPORT_ROWS = 10000

# Audit settings
AUDIT_LOG_RETENTION_DAYS = 365
LOG_SENSITIVE_OPERATIONS = True

# Development settings
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# External API settings (for future features)
EXCHANGE_RATE_API_ENABLED = False
EXCHANGE_RATE_UPDATE_INTERVAL = 3600  # seconds
QRIS_PAYMENT_ENABLED = False

# Backup settings
AUTO_BACKUP_ENABLED = False
BACKUP_INTERVAL_HOURS = 24
BACKUP_RETENTION_DAYS = 30

# Feature flags
FEATURES = {
    "email_notifications": False,
    "sms_notifications": False,
    "qr_payments": False,
    "api_access": False,
    "multi_branch": False,
    "advanced_analytics": True,
    "mobile_app": False
}

# Currency formatting
CURRENCY_SYMBOLS = {
    "IDR": "Rp",
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "SGD": "S$",
    "AUD": "A$",
    "MYR": "RM",
    "CNY": "¥",
    "SAR": "﷼",
    "THB": "฿"
}

# Error messages
ERROR_MESSAGES = {
    "authentication_required": "Please login to access this page",
    "permission_denied": "You don't have permission to access this feature",
    "invalid_credentials": "Invalid username or password",
    "session_expired": "Your session has expired, please login again",
    "database_error": "Database error occurred, please try again",
    "insufficient_inventory": "Insufficient inventory for this transaction",
    "invalid_amount": "Invalid amount entered",
    "connection_error": "Connection error, please check your network"
}

# Success messages
SUCCESS_MESSAGES = {
    "transaction_completed": "Transaction completed successfully",
    "user_created": "User created successfully",
    "currency_updated": "Currency rates updated successfully",
    "customer_added": "Customer added successfully",
    "inventory_updated": "Inventory updated successfully"
}

# Pagination settings
DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100

# File upload settings
MAX_FILE_SIZE_MB = 10
ALLOWED_FILE_TYPES = ["csv", "xlsx", "pdf"]