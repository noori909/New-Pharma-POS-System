"""
Main Entry Point Launcher for NQS POS v2.0 (New Pharma POS System)
Initializes database schemas, checks migrations, and starts the PyQt6 Desktop GUI.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from app.core.database import init_db
from app.ui.main_window import MainWindow


def main():
    # 1. Initialize SQLite Database & Schema Migrations
    try:
        init_db()
        print("Database initialized & schema migrations verified.")
    except Exception as e:
        print(f"Database Initialization Error: {e}")
        sys.exit(1)

    # 2. Start PyQt6 Application
    app = QApplication(sys.argv)
    app.setApplicationName("NQS POS v2.0")
    app.setOrganizationName("NQS Pharma")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
