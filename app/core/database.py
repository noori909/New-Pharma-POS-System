"""
Database Layer for NQS POS v2.0
Handles SQLite initialization, table creation, and connection pooling.
All user data is stored in %APPDATA%/NQS_POS/nqs_pos.db for machine independence and safety.
"""

import os
import sqlite3
from pathlib import Path


def get_app_data_dir() -> Path:
    """Returns absolute path to AppData directory for NQS POS."""
    appdata = os.getenv('APPDATA')
    if appdata:
        base_dir = Path(appdata) / "NQS_POS"
    else:
        base_dir = Path.home() / ".nqs_pos"
    
    base_dir.mkdir(parents=True, exist_ok=True)
    (base_dir / "backups").mkdir(parents=True, exist_ok=True)
    return base_dir


def get_db_path() -> Path:
    """Returns path to nqs_pos.db file."""
    return get_app_data_dir() / "nqs_pos.db"


def get_connection() -> sqlite3.Connection:
    """Creates a new SQLite database connection with row factory enabled."""
    conn = sqlite3.connect(get_db_path(), timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_db():
    """Initializes SQLite database schemas if not present."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Products Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        mrp REAL NOT NULL DEFAULT 0.0,
        stock INTEGER NOT NULL DEFAULT 0,
        reorder_level INTEGER NOT NULL DEFAULT 10,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Areas Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS areas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        region TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Sales Reps Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_reps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        phone TEXT DEFAULT '',
        email TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Customers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        phone TEXT DEFAULT '',
        address TEXT DEFAULT '',
        area_id INTEGER,
        discount_tier REAL NOT NULL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (area_id) REFERENCES areas(id) ON DELETE SET NULL
    );
    """)

    # 5. Invoices Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_number TEXT UNIQUE NOT NULL,
        seq_num INTEGER UNIQUE NOT NULL,
        customer_id INTEGER NOT NULL,
        customer_name TEXT NOT NULL,
        sales_rep_id INTEGER NOT NULL,
        sales_rep_name TEXT NOT NULL,
        area_name TEXT DEFAULT '',
        discount_tier REAL NOT NULL DEFAULT 0.0,
        subtotal REAL NOT NULL DEFAULT 0.0,
        discount_amount REAL NOT NULL DEFAULT 0.0,
        grand_total REAL NOT NULL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (sales_rep_id) REFERENCES sales_reps(id)
    );
    """)

    # 6. Invoice Items Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        mrp REAL NOT NULL,
        tp REAL NOT NULL,
        discount_percent REAL NOT NULL,
        final_rate REAL NOT NULL,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """)

    # 7. App Settings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """)

    # Set default settings if not exists
    default_settings = {
        'next_invoice_seq': '100',  # Configurable sequence start
        'smtp_email': '',
        'smtp_password': '',
        'recipient_emails': '',
        'gdrive_folder_id': '',
        'theme': 'dark',
        'last_eod_date': '',
        'business_name': 'NQS Pharmaceutical Distributors',
        'business_address': 'Warehouse Complex, Main Industrial Estate',
        'business_phone': '+92-300-1234567'
    }

    for key, val in default_settings.items():
        cursor.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES (?, ?);", (key, val))

    conn.commit()
    conn.close()
