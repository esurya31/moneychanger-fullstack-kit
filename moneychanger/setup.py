#!/usr/bin/env python3
"""
Money Changer Application Setup Script
Automated setup and initialization script
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def print_header():
    """Print setup header"""
    print("=" * 60)
    print("🏦 Money Changer Application Setup")
    print("=" * 60)
    print("Complete Foreign Exchange Management System")
    print("This script will set up the application for first-time use.")
    print("=" * 60)
    print()

def check_python_version():
    """Check Python version compatibility"""
    print("🔍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    print()

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = [
        "data",
        "logs",
        "exports",
        "backups"
    ]

    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

    print()

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing dependencies...")
    try:
        # Upgrade pip
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

        # Install requirements
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)
    print()

def initialize_database():
    """Initialize database and create tables"""
    print("🗄️ Initializing database...")
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

        # Import database modules
        from database.schema import db, DatabaseSchema
        from database.seed_data import seed_all_data

        # Initialize database schema
        print("   Creating database schema...")
        db.init_database()

        # Seed with initial data
        print("   Populating with sample data...")
        seed_all_data()

        print("✅ Database initialized successfully")

        # Verify data
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM currencies")
        currency_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM customers")
        customer_count = cursor.fetchone()[0]

        conn.close()

        print(f"   - {user_count} users created")
        print(f"   - {currency_count} currencies added")
        print(f"   - {customer_count} sample customers added")

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)
    print()

def create_env_file():
    """Create .env file with default settings"""
    print("⚙️ Creating environment configuration...")
    env_content = """# Money Changer Environment Configuration

# Debug mode (true/false)
DEBUG=false

# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Session timeout in hours
SESSION_TIMEOUT_HOURS=8

# Database settings
DATABASE_PATH=./data/moneychanger.db

# Business settings
LOW_STOCK_THRESHOLD=10
CRITICAL_STOCK_THRESHOLD=5

# Feature flags
EMAIL_NOTIFICATIONS=false
SMS_NOTIFICATIONS=false
QR_PAYMENTS=false
API_ACCESS=false
"""

    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ Created .env file with default settings")
    else:
        print("✅ .env file already exists")
    print()

def test_setup():
    """Test the setup by running basic imports"""
    print("🧪 Testing setup...")
    try:
        # Test database connection
        from database.schema import db
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        conn.close()
        print("✅ Database connection test passed")

        # Test core imports
        from utils.auth import SessionManager, RoleManager
        from utils.helpers import format_currency
        print("✅ Core module imports successful")

        # Test configuration
        import config
        print("✅ Configuration loaded successfully")

    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        sys.exit(1)
    print()

def print_completion_message():
    """Print completion message with next steps"""
    print("=" * 60)
    print("🎉 Setup Completed Successfully!")
    print("=" * 60)
    print()
    print("📋 Setup Summary:")
    print("✅ Directories created")
    print("✅ Dependencies installed")
    print("✅ Database initialized")
    print("✅ Sample data populated")
    print("✅ Configuration created")
    print()
    print("🚀 Next Steps:")
    print("1. Run the application:")
    print("   streamlit run app.py")
    print()
    print("2. Open your browser and navigate to:")
    print("   http://localhost:8501")
    print()
    print("👤 Default Login Credentials:")
    print("   Admin:    username: admin,    password: admin123")
    print("   Kasir:    username: cashier1,  password: cashier123")
    print("   Auditor:  username: auditor1,  password: auditor123")
    print()
    print("📚 Documentation:")
    print("   - README.md          : Overview and features")
    print("   - USER_GUIDE.md      : User manual")
    print("   - DEVELOPER_GUIDE.md : Development guide")
    print()
    print("⚠️  Important Security Notes:")
    print("   - Change default passwords after first login")
    print("   - Keep your login credentials secure")
    print("   - Regular backups are recommended")
    print()
    print("🆘 Need Help?")
    print("   - Check the documentation files")
    print("   - Review the troubleshooting section")
    print("   - Contact system administrator for support")
    print("=" * 60)

def main():
    """Main setup function"""
    print_header()

    try:
        check_python_version()
        create_directories()
        install_dependencies()
        initialize_database()
        create_env_file()
        test_setup()
        print_completion_message()
    except KeyboardInterrupt:
        print("\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()