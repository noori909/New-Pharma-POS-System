"""
Main Entry Point Launcher for New Quetta Surgical and Medicine Distribution (NQS POS v2.0)
Initializes database schemas, checks migrations, and starts the PyQt6 Desktop GUI.
"""

import sys
import os
import traceback
from pathlib import Path

# Ensure application root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def show_error_dialog(title: str, message: str):
    """Displays a graphical error dialog if the app fails to start."""
    try:
        from PyQt6.QtWidgets import QApplication, QMessageBox
        app = QApplication.instance() or QApplication(sys.argv)
        QMessageBox.critical(None, title, message)
    except Exception:
        # Fallback to Windows native MessageBox if PyQt fails
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, message, title, 0x10)  # MB_ICONERROR
        except Exception:
            print(f"{title}: {message}", file=sys.stderr)


def main():
    try:
        from app.core.database import init_db
        init_db()
        print("Database initialized & schema migrations verified.")
    except Exception as e:
        err_msg = f"Database Initialization Error:\n{traceback.format_exc()}"
        print(err_msg, file=sys.stderr)
        show_error_dialog("NQS POS - Database Error", err_msg)
        sys.exit(1)

    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from app.ui.main_window import MainWindow

        app = QApplication(sys.argv)
        app.setApplicationName("New Quetta Surgical POS")
        app.setOrganizationName("New Quetta Surgical")

        window = MainWindow()
        window.show()

        sys.exit(app.exec())

    except Exception as e:
        err_msg = f"Application Startup Error:\n{traceback.format_exc()}"
        print(err_msg, file=sys.stderr)
        show_error_dialog("NQS POS - Startup Error", err_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
