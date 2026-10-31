"""
Database Layer & Schema Migration Engine for New Quetta Surgical and Medicine Distribution (NQS POS v2.0)
Handles SQLite connection setup, initial table creation, and incremental schema migrations.
Stored in %APPDATA%/NQS_POS/nqs_pos.db for machine independence and data safety.
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
    (base_dir / "receipts").mkdir(parents=True, exist_ok=True)
    (base_dir / "reports").mkdir(parents=True, exist_ok=True)
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
    """Initializes SQLite database and runs incremental schema migrations."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Schema Migrations Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER PRIMARY KEY,
        description TEXT NOT NULL,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Discount Tiers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS discount_tiers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        percentage REAL NOT NULL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Products Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        mrp REAL NOT NULL DEFAULT 0.0,
        has_tp INTEGER NOT NULL DEFAULT 1,
        default_discount REAL NOT NULL DEFAULT 0.0,
        stock INTEGER NOT NULL DEFAULT 0,
        reorder_level INTEGER NOT NULL DEFAULT 10,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Areas Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS areas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        region TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. Sales Reps Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_reps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        phone TEXT DEFAULT '',
        email TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. Customers Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        phone TEXT DEFAULT '',
        address TEXT DEFAULT '',
        area_id INTEGER,
        discount_tier REAL NOT NULL DEFAULT 0.0,
        discount_tier_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (area_id) REFERENCES areas(id) ON DELETE SET NULL,
        FOREIGN KEY (discount_tier_id) REFERENCES discount_tiers(id) ON DELETE SET NULL
    );
    """)

    # 7. Invoices Table
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
        payment_mode TEXT NOT NULL DEFAULT 'Cash',
        subtotal REAL NOT NULL DEFAULT 0.0,
        discount_amount REAL NOT NULL DEFAULT 0.0,
        grand_total REAL NOT NULL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (customer_id) REFERENCES customers(id),
        FOREIGN KEY (sales_rep_id) REFERENCES sales_reps(id)
    );
    """)

    # 8. Invoice Items Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        mrp REAL NOT NULL,
        has_tp INTEGER NOT NULL DEFAULT 1,
        tp REAL NOT NULL,
        discount_percent REAL NOT NULL,
        final_rate REAL NOT NULL,
        quantity INTEGER NOT NULL,
        total_price REAL NOT NULL,
        FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
    """)

    # 9. App Settings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """)

    # Default App Settings
    default_settings = {
        'next_invoice_seq': '1',  # Starting value 1 -> NQS-001-DD-MM-YY
        'smtp_email': '',
        'smtp_password': '',
        'recipient_emails': '',
        'gdrive_folder_id': '',
        'theme': 'dark',
        'last_eod_date': '',
        'business_name': 'New Quetta Surgical and Medicine Distribution',
        'business_address': 'Ramzan Plaza Near Saleem Complex, Ptail Bagh. Quetta.',
        'business_phone': '0334-2045896',
        'business_email': 'newquettamedicalandsurgical@gmail.com',
        'warranty_text': (
            'Warranty: Under section 23(1) of the drug act 1976, I Nazir Ahmed being a person resident in Pakistan '
            'Carrying business at Ramzan plaza Patail Bagh Quetta under the name of New Quetta Surgical and Medicine Distribution '
            'being an authorized distributor do hereby give this warranty that drugs described in this invoice bill as sold by us '
            'do not contrivance in any way the provisions of section 23 of drug act 1976.'
        )
    }

    for key, val in default_settings.items():
        cursor.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES (?, ?);", (key, val))

    # Seed Default Discount Tiers if empty
    cursor.execute("SELECT COUNT(*) as count FROM discount_tiers;")
    if cursor.fetchone()['count'] == 0:
        default_tiers = [
            ("Standard (0%)", 0.0),
            ("Tier 1 (4%)", 4.0),
            ("Tier 2 (7%)", 7.0),
            ("Tier 3 (12%)", 12.0)
        ]
        for t_name, t_pct in default_tiers:
            cursor.execute("INSERT INTO discount_tiers (name, percentage) VALUES (?, ?);", (t_name, t_pct))

    conn.commit()

    # Run Schema Migrations
    run_migrations(conn)

    conn.close()


def run_migrations(conn: sqlite3.Connection):
    """
    Checks applied schema migration versions and executes pending incremental migrations.
    No Alembic dependency required.
    """
    cursor = conn.cursor()

    def is_applied(v_id: int) -> bool:
        cursor.execute("SELECT 1 FROM schema_migrations WHERE version = ?;", (v_id,))
        return cursor.fetchone() is not None

    def column_exists(table: str, col: str) -> bool:
        cursor.execute(f"PRAGMA table_info({table});")
        return any(r['name'] == col for r in cursor.fetchall())

    # Migration 1: Base Version Tracker
    if not is_applied(1):
        cursor.execute("INSERT INTO schema_migrations (version, description) VALUES (1, 'Initial Base Schema');")
        conn.commit()

    # Migration 2: Ensure perpetual invoice sequence is initialized
    if not is_applied(2):
        cursor.execute("INSERT OR IGNORE INTO app_settings (key, value) VALUES ('next_invoice_seq', '1');")
        cursor.execute("INSERT INTO schema_migrations (version, description) VALUES (2, 'Ensure starting invoice seq set to 1');")
        conn.commit()

    # Migration 3: Add has_tp and default_discount to products
    if not is_applied(3):
        if not column_exists('products', 'has_tp'):
            cursor.execute("ALTER TABLE products ADD COLUMN has_tp INTEGER NOT NULL DEFAULT 1;")
        if not column_exists('products', 'default_discount'):
            cursor.execute("ALTER TABLE products ADD COLUMN default_discount REAL NOT NULL DEFAULT 0.0;")
        cursor.execute("INSERT INTO schema_migrations (version, description) VALUES (3, 'Add has_tp and default_discount to products');")
        conn.commit()

    # Migration 4: Add payment_mode to invoices
    if not is_applied(4):
        if not column_exists('invoices', 'payment_mode'):
            cursor.execute("ALTER TABLE invoices ADD COLUMN payment_mode TEXT NOT NULL DEFAULT 'Cash';")
        cursor.execute("INSERT INTO schema_migrations (version, description) VALUES (4, 'Add payment_mode to invoices');")
        conn.commit()

    # Migration 5: Add has_tp to invoice_items
    if not is_applied(5):
        if not column_exists('invoice_items', 'has_tp'):
            cursor.execute("ALTER TABLE invoice_items ADD COLUMN has_tp INTEGER NOT NULL DEFAULT 1;")
        cursor.execute("INSERT INTO schema_migrations (version, description) VALUES (5, 'Add has_tp to invoice_items');")
        conn.commit()

    # Migration 6: Update store branding, contact, and warranty
    if not is_applied(6):
        cursor.execute("""
            UPDATE app_settings 
            SET value = 'New Quetta Surgical and Medicine Distribution' 
            WHERE key = 'business_name' AND (value = 'NQS Pharmaceutical Distributors' OR value = '');
        """)
        cursor.execute("""
            UPDATE app_settings 
            SET value = 'Ramzan Plaza Near Saleem Complex, Ptail Bagh. Quetta.' 
            WHERE key = 'business_address' AND (value LIKE '%Warehouse%' OR value = '');
        """)
        cursor.execute("""
            UPDATE app_settings 
            SET value = '0334-2045896' 
            WHERE key = 'business_phone' AND (value LIKE '%+92-300-1234567%' OR value = '');
        """)
        cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES ('business_email', 'newquettamedicalandsurgical@gmail.com');")
        cursor.execute("""
            INSERT OR REPLACE INTO app_settings (key, value) VALUES (
                'warranty_text', 
                'Warranty: Under section 23(1) of the drug act 1976, I Nazir Ahmed being a person resident in Pakistan Carrying business at Ramzan plaza Patail Bagh Quetta under the name of New Quetta Surgical and Medicine Distribution being an authorized distributor do hereby give this warranty that drugs described in this invoice bill as sold by us do not contrivance in any way the provisions of section 23 of drug act 1976.'
            );
        """)
        cursor.execute("INSERT INTO schema_migrations (version, description) VALUES (6, 'Update store branding, contact, and warranty');")
        conn.commit()
