"""
Database Models and Operations for Money Changer Application
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any
import sqlite3
import hashlib
import secrets
from .schema import DatabaseSchema

class UserModel:
    """User model with authentication and role management"""

    def __init__(self, db: DatabaseSchema):
        self.db = db

    def create_user(self, username: str, password: str, full_name: str,
                   email: str, role: str) -> int:
        """Create a new user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Hash password
        password_hash = self._hash_password(password)

        cursor.execute('''
            INSERT INTO users (username, password_hash, full_name, email, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, password_hash, full_name, email, role))

        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Log audit
        self.db.log_audit(
            user_id=user_id,
            action="CREATE_USER",
            table_name="users",
            record_id=user_id,
            new_values={"username": username, "full_name": full_name, "email": email, "role": role}
        )

        return user_id

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        password_hash = self._hash_password(password)

        cursor.execute('''
            SELECT id, username, full_name, email, role, is_active
            FROM users
            WHERE username = ? AND password_hash = ? AND is_active = 1
        ''', (username, password_hash))

        user = cursor.fetchone()
        conn.close()

        return dict(user) if user else None

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, username, full_name, email, role, is_active, created_at
            FROM users WHERE id = ?
        ''', (user_id,))

        user = cursor.fetchone()
        conn.close()

        return dict(user) if user else None

    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, username, full_name, email, role, is_active, created_at
            FROM users ORDER BY created_at DESC
        ''')

        users = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return users

    def update_user(self, user_id: int, **kwargs) -> bool:
        """Update user data"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get old values for audit
        old_user = self.get_user_by_id(user_id)

        set_clause = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [user_id]

        cursor.execute(f'''
            UPDATE users SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', values)

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()

        if success:
            self.db.log_audit(
                user_id=user_id,
                action="UPDATE_USER",
                table_name="users",
                record_id=user_id,
                old_values=old_user,
                new_values=kwargs
            )

        return success

    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt, hash_value = stored_hash.split(":")
            return hashlib.sha256((password + salt).encode()).hexdigest() == hash_value
        except:
            return False


class CurrencyModel:
    """Currency model for managing exchange rates"""

    def __init__(self, db: DatabaseSchema):
        self.db = db

    def create_currency(self, code: str, name: str, symbol: str,
                       buy_rate: float, sell_rate: float) -> int:
        """Create a new currency"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO currencies (code, name, symbol, buy_rate, sell_rate)
            VALUES (?, ?, ?, ?, ?)
        ''', (code.upper(), name, symbol, buy_rate, sell_rate))

        currency_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return currency_id

    def get_all_currencies(self) -> List[Dict]:
        """Get all active currencies"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, code, name, symbol, buy_rate, sell_rate, last_updated, is_active
            FROM currencies WHERE is_active = 1 ORDER BY code
        ''')

        currencies = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return currencies

    def get_currency_by_code(self, code: str) -> Optional[Dict]:
        """Get currency by code"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, code, name, symbol, buy_rate, sell_rate, last_updated, is_active
            FROM currencies WHERE code = ? AND is_active = 1
        ''', (code.upper(),))

        currency = cursor.fetchone()
        conn.close()

        return dict(currency) if currency else None

    def update_rates(self, code: str, buy_rate: float, sell_rate: float,
                    user_id: Optional[int] = None) -> bool:
        """Update currency exchange rates"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get old rates for audit and history
        old_currency = self.get_currency_by_code(code)

        cursor.execute('''
            UPDATE currencies SET buy_rate = ?, sell_rate = ?, last_updated = CURRENT_TIMESTAMP
            WHERE code = ? AND is_active = 1
        ''', (buy_rate, sell_rate, code.upper()))

        success = cursor.rowcount > 0

        # Add to rate history
        if success:
            cursor.execute('''
                INSERT INTO exchange_rate_history (currency_code, buy_rate, sell_rate, updated_by)
                VALUES (?, ?, ?, ?)
            ''', (code.upper(), buy_rate, sell_rate, user_id))

        conn.commit()
        conn.close()

        if success:
            self.db.log_audit(
                user_id=user_id,
                action="UPDATE_RATES",
                table_name="currencies",
                record_id=old_currency['id'],
                old_values=old_currency,
                new_values={"buy_rate": buy_rate, "sell_rate": sell_rate}
            )

        return success


class CustomerModel:
    """Customer model for managing customer data"""

    def __init__(self, db: DatabaseSchema):
        self.db = db

    def create_customer(self, customer_code: str, full_name: str,
                       identity_number: str = None, country: str = None,
                       phone: str = None, email: str = None,
                       address: str = None) -> int:
        """Create a new customer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO customers (customer_code, full_name, identity_number,
                                 country, phone, email, address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (customer_code, full_name, identity_number, country,
              phone, email, address))

        customer_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Log audit
        self.db.log_audit(
            user_id=None,  # System created
            action="CREATE_CUSTOMER",
            table_name="customers",
            record_id=customer_id,
            new_values={"customer_code": customer_code, "full_name": full_name}
        )

        return customer_id

    def get_all_customers(self) -> List[Dict]:
        """Get all active customers"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, customer_code, full_name, identity_number, country,
                   phone, email, address, is_active, created_at
            FROM customers WHERE is_active = 1 ORDER BY full_name
        ''')

        customers = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return customers

    def get_customer_by_id(self, customer_id: int) -> Optional[Dict]:
        """Get customer by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, customer_code, full_name, identity_number, country,
                   phone, email, address, is_active, created_at
            FROM customers WHERE id = ? AND is_active = 1
        ''', (customer_id,))

        customer = cursor.fetchone()
        conn.close()

        return dict(customer) if customer else None

    def search_customers(self, query: str) -> List[Dict]:
        """Search customers by name or code"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, customer_code, full_name, identity_number, country, phone, email
            FROM customers
            WHERE is_active = 1 AND
                  (full_name LIKE ? OR customer_code LIKE ? OR identity_number LIKE ?)
            ORDER BY full_name
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))

        customers = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return customers


class TransactionModel:
    """Transaction model for managing money exchange transactions"""

    def __init__(self, db: DatabaseSchema):
        self.db = db

    def create_transaction(self, transaction_number: str, transaction_type: str,
                          customer_id: int, user_id: int, currency_code: str,
                          foreign_amount: float, rate: float, idr_amount: float,
                          total_notes: int = None, notes: str = None) -> int:
        """Create a new transaction"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO transactions (transaction_number, transaction_type,
                                        customer_id, user_id, currency_code,
                                        foreign_amount, rate, idr_amount,
                                        total_notes, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (transaction_number, transaction_type, customer_id, user_id,
                  currency_code.upper(), foreign_amount, rate, idr_amount,
                  total_notes, notes))

            transaction_id = cursor.lastrowid
            conn.commit()

            # Log audit
            self.db.log_audit(
                user_id=user_id,
                action="CREATE_TRANSACTION",
                table_name="transactions",
                record_id=transaction_id,
                new_values={
                    "transaction_number": transaction_number,
                    "transaction_type": transaction_type,
                    "foreign_amount": foreign_amount,
                    "idr_amount": idr_amount
                }
            )

            return transaction_id

        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    def get_transactions_by_date_range(self, start_date: date, end_date: date,
                                      user_id: Optional[int] = None) -> List[Dict]:
        """Get transactions within date range"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT t.*, c.full_name as customer_name, u.full_name as user_name,
                   cur.name as currency_name, cur.symbol
            FROM transactions t
            JOIN customers c ON t.customer_id = c.id
            JOIN users u ON t.user_id = u.id
            JOIN currencies cur ON t.currency_code = cur.code
            WHERE DATE(t.transaction_date) BETWEEN ? AND ?
        '''
        params = [start_date, end_date]

        if user_id:
            query += ' AND t.user_id = ?'
            params.append(user_id)

        query += ' ORDER BY t.transaction_date DESC'

        cursor.execute(query, params)
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return transactions

    def get_transaction_by_number(self, transaction_number: str) -> Optional[Dict]:
        """Get transaction by number"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT t.*, c.full_name as customer_name, c.customer_code,
                   u.full_name as user_name, cur.name as currency_name, cur.symbol
            FROM transactions t
            JOIN customers c ON t.customer_id = c.id
            JOIN users u ON t.user_id = u.id
            JOIN currencies cur ON t.currency_code = cur.code
            WHERE t.transaction_number = ?
        ''', (transaction_number,))

        transaction = cursor.fetchone()
        conn.close()

        return dict(transaction) if transaction else None

    def generate_transaction_number(self) -> str:
        """Generate unique transaction number"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        today = datetime.now().strftime("%Y%m%d")

        cursor.execute('''
            SELECT COUNT(*) as count FROM transactions
            WHERE DATE(transaction_date) = DATE('now')
        ''')

        count = cursor.fetchone()['count']
        sequence = str(count + 1).zfill(4)

        conn.close()
        return f"TRX{today}{sequence}"


class InventoryModel:
    """Inventory model for managing denomination stock"""

    def __init__(self, db: DatabaseSchema):
        self.db = db

    def get_inventory_by_currency(self, currency_code: str) -> List[Dict]:
        """Get inventory for specific currency"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT denomination, quantity, last_updated
            FROM denomination_inventory
            WHERE currency_code = ?
            ORDER BY denomination DESC
        ''', (currency_code.upper(),))

        inventory = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return inventory

    def get_all_inventory(self) -> List[Dict]:
        """Get all inventory with currency info"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT di.*, c.name as currency_name, c.symbol,
                   (di.quantity * di.denomination * c.buy_rate) as idr_value
            FROM denomination_inventory di
            JOIN currencies c ON di.currency_code = c.code
            WHERE c.is_active = 1
            ORDER BY c.code, di.denomination DESC
        ''')

        inventory = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return inventory

    def update_inventory(self, currency_code: str, denomination: float,
                        quantity_change: int, user_id: Optional[int] = None) -> bool:
        """Update inventory quantity"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # Get current quantity
            cursor.execute('''
                SELECT quantity FROM denomination_inventory
                WHERE currency_code = ? AND denomination = ?
            ''', (currency_code.upper(), denomination))

            result = cursor.fetchone()

            if result:
                new_quantity = result['quantity'] + quantity_change
                if new_quantity < 0:
                    raise ValueError("Insufficient inventory")

                cursor.execute('''
                    UPDATE denomination_inventory
                    SET quantity = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE currency_code = ? AND denomination = ?
                ''', (new_quantity, currency_code.upper(), denomination))
            else:
                if quantity_change < 0:
                    raise ValueError("Insufficient inventory")

                cursor.execute('''
                    INSERT INTO denomination_inventory (currency_code, denomination, quantity)
                    VALUES (?, ?, ?)
                ''', (currency_code.upper(), denomination, quantity_change))

            conn.commit()

            # Log audit
            self.db.log_audit(
                user_id=user_id,
                action="UPDATE_INVENTORY",
                table_name="denomination_inventory",
                new_values={
                    "currency_code": currency_code,
                    "denomination": denomination,
                    "quantity_change": quantity_change
                }
            )

            return True

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def get_currency_summary(self) -> List[Dict]:
        """Get inventory summary by currency"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT di.currency_code, c.name as currency_name, c.symbol,
                   SUM(di.quantity * di.denomination) as total_foreign_amount,
                   SUM(di.quantity * di.denomination * c.buy_rate) as total_idr_value,
                   COUNT(*) as denomination_count
            FROM denomination_inventory di
            JOIN currencies c ON di.currency_code = c.code
            WHERE c.is_active = 1 AND di.quantity > 0
            GROUP BY di.currency_code, c.name, c.symbol
            ORDER BY total_idr_value DESC
        ''')

        summary = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return summary


class ReportModel:
    """Report model for generating various reports"""

    def __init__(self, db: DatabaseSchema):
        self.db = db

    def get_daily_summary(self, report_date: date) -> Dict:
        """Get daily transaction summary"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                COUNT(*) as total_transactions,
                COUNT(CASE WHEN transaction_type = 'BUY' THEN 1 END) as buy_transactions,
                COUNT(CASE WHEN transaction_type = 'SELL' THEN 1 END) as sell_transactions,
                SUM(CASE WHEN transaction_type = 'BUY' THEN idr_amount ELSE 0 END) as total_buy_idr,
                SUM(CASE WHEN transaction_type = 'SELL' THEN idr_amount ELSE 0 END) as total_sell_idr,
                SUM(foreign_amount) as total_foreign_amount
            FROM transactions
            WHERE DATE(transaction_date) = ? AND status = 'COMPLETED'
        ''', (report_date,))

        summary = dict(cursor.fetchone())
        conn.close()

        return summary

    def get_profit_loss_report(self, start_date: date, end_date: date) -> List[Dict]:
        """Get profit/loss report by currency"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                t.currency_code,
                c.name as currency_name,
                SUM(CASE WHEN t.transaction_type = 'SELL' THEN t.foreign_amount ELSE 0 END) as total_sell,
                SUM(CASE WHEN t.transaction_type = 'BUY' THEN t.foreign_amount ELSE 0 END) as total_buy,
                c.sell_rate,
                c.buy_rate,
                (SUM(CASE WHEN t.transaction_type = 'SELL' THEN t.foreign_amount ELSE 0 END) * c.sell_rate) -
                (SUM(CASE WHEN t.transaction_type = 'BUY' THEN t.foreign_amount ELSE 0 END) * c.buy_rate) as gross_profit
            FROM transactions t
            JOIN currencies c ON t.currency_code = c.code
            WHERE DATE(t.transaction_date) BETWEEN ? AND ? AND t.status = 'COMPLETED'
            GROUP BY t.currency_code, c.name, c.sell_rate, c.buy_rate
            ORDER BY gross_profit DESC
        ''', (start_date, end_date))

        profit_loss = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return profit_loss

    def get_audit_logs(self, start_date: date, end_date: date,
                      user_id: Optional[int] = None) -> List[Dict]:
        """Get audit logs within date range"""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        query = '''
            SELECT al.*, u.full_name as user_name
            FROM audit_logs al
            LEFT JOIN users u ON al.user_id = u.id
            WHERE DATE(al.timestamp) BETWEEN ? AND ?
        '''
        params = [start_date, end_date]

        if user_id:
            query += ' AND al.user_id = ?'
            params.append(user_id)

        query += ' ORDER BY al.timestamp DESC'

        cursor.execute(query, params)
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return logs

# Export model instances
from .schema import db

user_model = UserModel(db)
currency_model = CurrencyModel(db)
customer_model = CustomerModel(db)
transaction_model = TransactionModel(db)
inventory_model = InventoryModel(db)
report_model = ReportModel(db)

__all__ = [
    'UserModel', 'CurrencyModel', 'CustomerModel', 'TransactionModel',
    'InventoryModel', 'ReportModel', 'user_model', 'currency_model',
    'customer_model', 'transaction_model', 'inventory_model', 'report_model'
]