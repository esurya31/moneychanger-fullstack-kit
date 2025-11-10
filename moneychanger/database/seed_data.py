"""
Seed data script for Money Changer application
Populates database with initial currencies, users, and sample data
"""

from datetime import datetime, date
from .models import user_model, currency_model, customer_model, inventory_model

def create_default_users():
    """Create default users with different roles"""
    print("Creating default users...")

    # Admin user
    admin_id = user_model.create_user(
        username="admin",
        password="admin123",
        full_name="Administrator",
        email="admin@moneychanger.com",
        role="Admin"
    )
    print(f"Created admin user with ID: {admin_id}")

    # Cashier user
    cashier_id = user_model.create_user(
        username="cashier1",
        password="cashier123",
        full_name="John Cashier",
        email="cashier@moneychanger.com",
        role="Kasir"
    )
    print(f"Created cashier user with ID: {cashier_id}")

    # Auditor user
    auditor_id = user_model.create_user(
        username="auditor1",
        password="auditor123",
        full_name="Jane Auditor",
        email="auditor@moneychanger.com",
        role="Auditor"
    )
    print(f"Created auditor user with ID: {auditor_id}")

    return {
        'admin_id': admin_id,
        'cashier_id': cashier_id,
        'auditor_id': auditor_id
    }

def create_default_currencies():
    """Create default currencies with current exchange rates"""
    print("Creating default currencies...")

    currencies_data = [
        {
            'code': 'USD',
            'name': 'United States Dollar',
            'symbol': '$',
            'buy_rate': 15850.00,
            'sell_rate': 15950.00
        },
        {
            'code': 'EUR',
            'name': 'Euro',
            'symbol': '€',
            'buy_rate': 17250.00,
            'sell_rate': 17350.00
        },
        {
            'code': 'GBP',
            'name': 'British Pound Sterling',
            'symbol': '£',
            'buy_rate': 20250.00,
            'sell_rate': 20350.00
        },
        {
            'code': 'JPY',
            'name': 'Japanese Yen',
            'symbol': '¥',
            'buy_rate': 107.50,
            'sell_rate': 108.50
        },
        {
            'code': 'SGD',
            'name': 'Singapore Dollar',
            'symbol': 'S$',
            'buy_rate': 11750.00,
            'sell_rate': 11850.00
        },
        {
            'code': 'AUD',
            'name': 'Australian Dollar',
            'symbol': 'A$',
            'buy_rate': 10450.00,
            'sell_rate': 10550.00
        },
        {
            'code': 'MYR',
            'name': 'Malaysian Ringgit',
            'symbol': 'RM',
            'buy_rate': 3550.00,
            'sell_rate': 3650.00
        },
        {
            'code': 'CNY',
            'name': 'Chinese Yuan',
            'symbol': '¥',
            'buy_rate': 2180.00,
            'sell_rate': 2280.00
        },
        {
            'code': 'SAR',
            'name': 'Saudi Riyal',
            'symbol': '﷼',
            'buy_rate': 4220.00,
            'sell_rate': 4320.00
        },
        {
            'code': 'THB',
            'name': 'Thai Baht',
            'symbol': '฿',
            'buy_rate': 450.00,
            'sell_rate': 460.00
        }
    ]

    currency_ids = {}
    for currency_data in currencies_data:
        currency_id = currency_model.create_currency(**currency_data)
        currency_ids[currency_data['code']] = currency_id
        print(f"Created currency {currency_data['code']} - {currency_data['name']}")

    return currency_ids

def create_sample_customers():
    """Create sample customers"""
    print("Creating sample customers...")

    customers_data = [
        {
            'customer_code': 'CUST001',
            'full_name': 'Budi Santoso',
            'identity_number': '3171051234560001',
            'country': 'Indonesia',
            'phone': '+628121234567',
            'email': 'budi.santoso@email.com',
            'address': 'Jakarta, Indonesia'
        },
        {
            'customer_code': 'CUST002',
            'full_name': 'Sarah Johnson',
            'identity_number': 'US123456789',
            'country': 'United States',
            'phone': '+11234567890',
            'email': 'sarah.j@email.com',
            'address': 'New York, USA'
        },
        {
            'customer_code': 'CUST003',
            'full_name': 'Tanaka Hiroshi',
            'identity_number': 'JP987654321',
            'country': 'Japan',
            'phone': '+819012345678',
            'email': 'tanaka@email.jp',
            'address': 'Tokyo, Japan'
        },
        {
            'customer_code': 'CUST004',
            'full_name': 'Muhammad Rahman',
            'identity_number': 'MY456789012',
            'country': 'Malaysia',
            'phone': '+60123456789',
            'email': 'rahman@email.my',
            'address': 'Kuala Lumpur, Malaysia'
        },
        {
            'customer_code': 'CUST005',
            'full_name': 'Chen Wei',
            'identity_number': 'CN789012345',
            'country': 'China',
            'phone': '+861234567890',
            'email': 'chen.wei@email.cn',
            'address': 'Beijing, China'
        },
        {
            'customer_code': 'CUST006',
            'full_name': 'John Smith',
            'identity_number': 'UK567890123',
            'country': 'United Kingdom',
            'phone': '+447890123456',
            'email': 'john.smith@email.co.uk',
            'address': 'London, UK'
        },
        {
            'customer_code': 'CUST007',
            'full_name': 'Siti Nurhaliza',
            'identity_number': '3171059876540002',
            'country': 'Indonesia',
            'phone': '+6282298765432',
            'email': 'siti.n@email.com',
            'address': 'Surabaya, Indonesia'
        },
        {
            'customer_code': 'CUST008',
            'full_name': 'Michael Brown',
            'identity_number': 'AU345678901',
            'country': 'Australia',
            'phone': '+61412345678',
            'email': 'michael.b@email.com.au',
            'address': 'Sydney, Australia'
        }
    ]

    customer_ids = {}
    for customer_data in customers_data:
        customer_id = customer_model.create_customer(**customer_data)
        customer_ids[customer_data['customer_code']] = customer_id
        print(f"Created customer {customer_data['customer_code']} - {customer_data['full_name']}")

    return customer_ids

def create_initial_inventory():
    """Create initial inventory for each currency"""
    print("Creating initial inventory...")

    # Define denominations for each currency
    currency_denominations = {
        'USD': [100, 50, 20, 10, 5, 1],
        'EUR': [500, 200, 100, 50, 20, 10, 5],
        'GBP': [50, 20, 10, 5],
        'JPY': [10000, 5000, 2000, 1000],
        'SGD': [1000, 100, 50, 10, 5, 2],
        'AUD': [100, 50, 20, 10, 5],
        'MYR': [100, 50, 20, 10, 5, 1],
        'CNY': [100, 50, 20, 10, 5, 1],
        'SAR': [500, 200, 100, 50, 20, 10, 5, 1],
        'THB': [1000, 500, 100, 50, 20]
    }

    from .schema import db
    conn = db.get_connection()
    cursor = conn.cursor()

    for currency_code, denominations in currency_denominations.items():
        for denomination in denominations:
            # Random initial quantity between 10 and 100
            import random
            initial_quantity = random.randint(10, 100)

            cursor.execute('''
                INSERT OR IGNORE INTO denomination_inventory (currency_code, denomination, quantity)
                VALUES (?, ?, ?)
            ''', (currency_code, denomination, initial_quantity))

            print(f"Created inventory for {currency_code} {denomination}: {initial_quantity} units")

    conn.commit()
    conn.close()

def seed_all_data():
    """Seed all data into database"""
    print("=" * 50)
    print("SEEDING MONEY CHANGER DATABASE")
    print("=" * 50)

    try:
        # Create all data
        user_ids = create_default_users()
        currency_ids = create_default_currencies()
        customer_ids = create_sample_customers()
        create_initial_inventory()

        print("\n" + "=" * 50)
        print("DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"Users created: {len(user_ids)}")
        print(f"Currencies created: {len(currency_ids)}")
        print(f"Customers created: {len(customer_ids)}")
        print("\nDefault login credentials:")
        print("- Admin: admin / admin123")
        print("- Cashier: cashier1 / cashier123")
        print("- Auditor: auditor1 / auditor123")

    except Exception as e:
        print(f"\nError seeding data: {e}")
        raise

if __name__ == "__main__":
    seed_all_data()