#!/usr/bin/env python3
"""
Money Changer Application Runner
Convenient script to run the application with proper environment setup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_setup():
    """Check if the application has been properly set up"""
    if not Path("data/moneychanger.db").exists():
        print("❌ Database not found. Please run setup first:")
        print("   python setup.py")
        return False
    return True

def main():
    """Run the Money Changer application"""
    # Add current directory to Python path
    current_dir = Path(__file__).parent.resolve()
    sys.path.insert(0, str(current_dir))

    # Check if setup has been completed
    if not check_setup():
        sys.exit(1)

    # Set environment variables
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "false"
    os.environ["STREAMLIT_SERVER_PORT"] = "8501"

    print("🏦 Starting Money Changer Application...")
    print("📍 Opening in browser at: http://localhost:8501")
    print("🔧 To stop the application, press Ctrl+C")
    print()

    try:
        # Run streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()