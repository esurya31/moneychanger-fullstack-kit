"""
Database Schema for Money Changer Application
SQLite database with complete schema for all entities
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

class DatabaseSchema:
    """Complete database schema for Money Changer application"""

    def __init__(self, db_path: str = "moneychanger.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        return conn

    def init_database(self):
        """Initialize database with all tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE,
                role VARCHAR(20) NOT NULL CHECK (role IN ('Admin', 'Kasir', 'Auditor')),
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create Currencies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS currencies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code VARCHAR(3) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                symbol VARCHAR(10),
                buy_rate DECIMAL(15, 4) NOT NULL,
                sell_rate DECIMAL(15, 4) NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create Customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_code VARCHAR(20) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                identity_number VARCHAR(50),
                country VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(100),
                address TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_number VARCHAR(50) UNIQUE NOT NULL,
                transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('BUY', 'SELL')),
                customer_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                currency_code VARCHAR(3) NOT NULL,
                foreign_amount DECIMAL(15, 2) NOT NULL,
                rate DECIMAL(15, 4) NOT NULL,
                idr_amount DECIMAL(15, 2) NOT NULL,
                total_notes INTEGER,
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                status VARCHAR(20) DEFAULT 'COMPLETED',
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (currency_code) REFERENCES currencies(code)
            )
        ''')

        # Create Denomination Inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS denomination_inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency_code VARCHAR(3) NOT NULL,
                denomination DECIMAL(15, 2) NOT NULL,
                quantity INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (currency_code) REFERENCES currencies(code),
                UNIQUE(currency_code, denomination)
            )
        ''')

        # Create Transaction Denominations table (for tracking specific denominations used in transactions)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transaction_denominations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id INTEGER NOT NULL,
                currency_code VARCHAR(3) NOT NULL,
                denomination DECIMAL(15, 2) NOT NULL,
                quantity INTEGER NOT NULL,
                FOREIGN KEY (transaction_id) REFERENCES transactions(id),
                FOREIGN KEY (currency_code) REFERENCES currencies(code)
            )
        ''')

        # Create Audit Logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action VARCHAR(50) NOT NULL,
                table_name VARCHAR(50),
                record_id INTEGER,
                old_values TEXT,
                new_values TEXT,
                ip_address VARCHAR(45),
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')

        # Create Exchange Rate History table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exchange_rate_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                currency_code VARCHAR(3) NOT NULL,
                buy_rate DECIMAL(15, 4) NOT NULL,
                sell_rate DECIMAL(15, 4) NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_by INTEGER,
                FOREIGN KEY (currency_code) REFERENCES currencies(code),
                FOREIGN KEY (updated_by) REFERENCES users(id)
            )
        ''')

        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_currency ON transactions(currency_code)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_customers_code ON customers(customer_code)",
            "CREATE INDEX IF NOT EXISTS idx_denomination_inventory_currency ON denomination_inventory(currency_code)"
        ]

        for index in indexes:
            cursor.execute(index)

        conn.commit()
        conn.close()

    def log_audit(self, user_id: Optional[int], action: str, table_name: Optional[str] = None,
                  record_id: Optional[int] = None, old_values: Optional[Dict] = None,
                  new_values: Optional[Dict] = None, ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None):
        """Log audit trail"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO audit_logs (user_id, action, table_name, record_id, old_values, new_values, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, action, table_name, record_id,
            json.dumps(old_values) if old_values else None,
            json.dumps(new_values) if new_values else None,
            ip_address, user_agent
        ))

        conn.commit()
        conn.close()

# Initialize database instance
db = DatabaseSchema()

# Export for use in other modules
__all__ = ['DatabaseSchema', 'db']