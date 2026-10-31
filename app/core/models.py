"""
Data Models and Data Access Objects (DAO) for New Quetta Surgical and Medicine Distribution (NQS POS v2.0)
Handles all database operations for Products, Customers, Discount Tiers, Sales Reps, Areas, Invoices, and Reports.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from app.core.database import get_connection
from app.core.pricing import calculate_tp, calculate_final_rate, calculate_line_total, compute_cart_summary


# ==========================================
# APP SETTINGS
# ==========================================

def get_setting(key: str, default: str = "") -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM app_settings WHERE key = ?;", (key,))
    row = cursor.fetchone()
    conn.close()
    return row['value'] if row else default


def set_setting(key: str, value: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?);", (key, str(value)))
    conn.commit()
    conn.close()


def get_all_settings() -> Dict[str, str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT key, value FROM app_settings;")
    rows = cursor.fetchall()
    conn.close()
    return {row['key']: row['value'] for row in rows}


# ==========================================
# DISCOUNT TIERS DAO
# ==========================================

def get_all_discount_tiers() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM discount_tiers ORDER BY percentage ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_discount_tier(name: str, percentage: float) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO discount_tiers (name, percentage) VALUES (?, ?);", (name.strip(), float(percentage)))
    tier_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return tier_id


def update_discount_tier(tier_id: int, name: str, percentage: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE discount_tiers SET name = ?, percentage = ? WHERE id = ?;", (name.strip(), float(percentage), int(tier_id)))
    conn.commit()
    conn.close()


def delete_discount_tier(tier_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM discount_tiers WHERE id = ?;", (int(tier_id),))
    conn.commit()
    conn.close()


# ==========================================
# PRODUCTS DAO
# ==========================================

def get_all_products(search_query: str = "") -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    if search_query.strip():
        term = f"%{search_query.strip()}%"
        cursor.execute("""
            SELECT * FROM products 
            WHERE name LIKE ? 
            ORDER BY name ASC;
        """, (term,))
    else:
        cursor.execute("SELECT * FROM products ORDER BY name ASC;")
    
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        item = dict(r)
        has_tp = bool(item.get('has_tp', 1))
        item['has_tp'] = has_tp
        item['default_discount'] = float(item.get('default_discount', 0.0))
        item['tp'] = calculate_tp(item['mrp'], has_tp=has_tp)
        item['is_low_stock'] = item['stock'] <= item['reorder_level']
        result.append(item)
    return result


def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?;", (product_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    item = dict(row)
    has_tp = bool(item.get('has_tp', 1))
    item['has_tp'] = has_tp
    item['default_discount'] = float(item.get('default_discount', 0.0))
    item['tp'] = calculate_tp(item['mrp'], has_tp=has_tp)
    item['is_low_stock'] = item['stock'] <= item['reorder_level']
    return item


def add_product(name: str, mrp: float, stock: int, reorder_level: int, has_tp: bool = True, default_discount: float = 0.0) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO products (name, mrp, stock, reorder_level, has_tp, default_discount)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (name.strip(), float(mrp), int(stock), int(reorder_level), 1 if has_tp else 0, float(default_discount)))
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return product_id


def update_product(product_id: int, name: str, mrp: float, stock: int, reorder_level: int, has_tp: bool = True, default_discount: float = 0.0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products 
        SET name = ?, mrp = ?, stock = ?, reorder_level = ?, has_tp = ?, default_discount = ?
        WHERE id = ?;
    """, (name.strip(), float(mrp), int(stock), int(reorder_level), 1 if has_tp else 0, float(default_discount), int(product_id)))
    conn.commit()
    conn.close()


def update_product_stock(product_id: int, new_total_stock: int):
    """Updates exact stock level or adds to current stock."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE products 
        SET stock = ?
        WHERE id = ?;
    """, (int(new_total_stock), int(product_id)))
    conn.commit()
    conn.close()


def delete_product(product_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?;", (int(product_id),))
    conn.commit()
    conn.close()


def get_low_stock_products() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM products 
        WHERE stock <= reorder_level 
        ORDER BY stock ASC, name ASC;
    """)
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        item = dict(r)
        has_tp = bool(item.get('has_tp', 1))
        item['has_tp'] = has_tp
        item['default_discount'] = float(item.get('default_discount', 0.0))
        item['tp'] = calculate_tp(item['mrp'], has_tp=has_tp)
        item['is_low_stock'] = True
        result.append(item)
    return result


# ==========================================
# AREAS DAO
# ==========================================

def get_all_areas() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM areas ORDER BY name ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_area(name: str, region: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO areas (name, region) VALUES (?, ?);", (name.strip(), region.strip()))
    area_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return area_id


def update_area(area_id: int, name: str, region: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE areas SET name = ?, region = ? WHERE id = ?;", (name.strip(), region.strip(), int(area_id)))
    conn.commit()
    conn.close()


def delete_area(area_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM areas WHERE id = ?;", (int(area_id),))
    conn.commit()
    conn.close()


# ==========================================
# SALES REPS DAO
# ==========================================

def get_all_sales_reps() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sales_reps ORDER BY name ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_sales_rep(name: str, phone: str = "", email: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sales_reps (name, phone, email) VALUES (?, ?, ?);", (name.strip(), phone.strip(), email.strip()))
    rep_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rep_id


def update_sales_rep(rep_id: int, name: str, phone: str = "", email: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE sales_reps SET name = ?, phone = ?, email = ? WHERE id = ?;", 
                   (name.strip(), phone.strip(), email.strip(), int(rep_id)))
    conn.commit()
    conn.close()


def delete_sales_rep(rep_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sales_reps WHERE id = ?;", (int(rep_id),))
    conn.commit()
    conn.close()


# ==========================================
# CUSTOMERS DAO
# ==========================================

def get_all_customers(search_query: str = "") -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    if search_query.strip():
        term = f"%{search_query.strip()}%"
        cursor.execute("""
            SELECT c.*, a.name AS area_name, dt.name AS tier_name
            FROM customers c
            LEFT JOIN areas a ON c.area_id = a.id
            LEFT JOIN discount_tiers dt ON c.discount_tier_id = dt.id
            WHERE c.name LIKE ? OR c.phone LIKE ?
            ORDER BY c.name ASC;
        """, (term, term))
    else:
        cursor.execute("""
            SELECT c.*, a.name AS area_name, dt.name AS tier_name
            FROM customers c
            LEFT JOIN areas a ON c.area_id = a.id
            LEFT JOIN discount_tiers dt ON c.discount_tier_id = dt.id
            ORDER BY c.name ASC;
        """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_customer_by_id(customer_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, a.name AS area_name, dt.name AS tier_name
        FROM customers c
        LEFT JOIN areas a ON c.area_id = a.id
        LEFT JOIN discount_tiers dt ON c.discount_tier_id = dt.id
        WHERE c.id = ?;
    """, (customer_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def add_customer(name: str, phone: str, address: str, area_id: Optional[int], discount_tier: float, discount_tier_id: Optional[int] = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO customers (name, phone, address, area_id, discount_tier, discount_tier_id)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (name.strip(), phone.strip(), address.strip(), area_id, float(discount_tier), discount_tier_id))
    cust_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return cust_id


def update_customer(customer_id: int, name: str, phone: str, address: str, area_id: Optional[int], discount_tier: float, discount_tier_id: Optional[int] = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE customers 
        SET name = ?, phone = ?, address = ?, area_id = ?, discount_tier = ?, discount_tier_id = ?
        WHERE id = ?;
    """, (name.strip(), phone.strip(), address.strip(), area_id, float(discount_tier), discount_tier_id, int(customer_id)))
    conn.commit()
    conn.close()


def delete_customer(customer_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id = ?;", (int(customer_id),))
    conn.commit()
    conn.close()


# ==========================================
# INVOICING ENGINE DAO
# ==========================================

def preview_next_invoice_number() -> str:
    """Returns projected next invoice number string formatted as NQS-001-DD-MM-YY."""
    seq_str = get_setting('next_invoice_seq', '1')
    try:
        seq = int(seq_str)
    except ValueError:
        seq = 1
    now = datetime.now()
    return f"NQS-{seq:03d}-{now.strftime('%d-%m-%y')}"


def create_invoice(customer_id: int, sales_rep_id: int, cart_items: List[Dict[str, Any]], payment_mode: str = "Cash") -> Dict[str, Any]:
    """
    Transactionally creates a new invoice:
    1. Fetches Customer & Sales Rep details
    2. Increments & formats perpetual invoice sequence ID (e.g. NQS-001-14-08-26 starting at 1)
    3. Calculates line totals & grand total taking into account TP or MRP and custom discount %
    4. Deducts stock from products
    5. Saves invoice with payment_mode ('Cash' or 'Credit') and invoice_items
    """
    if not cart_items:
        raise ValueError("Cannot create invoice with empty cart items.")

    valid_payment_mode = "Credit" if str(payment_mode).strip().lower() == "credit" else "Cash"

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("BEGIN TRANSACTION;")

        # Fetch customer
        cursor.execute("""
            SELECT c.*, a.name AS area_name
            FROM customers c
            LEFT JOIN areas a ON c.area_id = a.id
            WHERE c.id = ?;
        """, (customer_id,))
        cust = cursor.fetchone()
        if not cust:
            raise ValueError(f"Customer ID {customer_id} not found.")

        # Fetch sales rep
        cursor.execute("SELECT * FROM sales_reps WHERE id = ?;", (sales_rep_id,))
        rep = cursor.fetchone()
        if not rep:
            raise ValueError(f"Sales Rep ID {sales_rep_id} not found.")

        # Fetch & increment perpetual invoice sequence (initialized to 1)
        cursor.execute("SELECT value FROM app_settings WHERE key = 'next_invoice_seq';")
        seq_row = cursor.fetchone()
        seq_num = int(seq_row['value']) if seq_row else 1
        
        now = datetime.now()
        invoice_number = f"NQS-{seq_num:03d}-{now.strftime('%d-%m-%y')}"

        # Calculate totals
        summary = compute_cart_summary(cart_items)

        # Insert Invoice header
        cursor.execute("""
            INSERT INTO invoices (
                invoice_number, seq_num, customer_id, customer_name,
                sales_rep_id, sales_rep_name, area_name, discount_tier,
                payment_mode, subtotal, discount_amount, grand_total, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            invoice_number,
            seq_num,
            cust['id'],
            cust['name'],
            rep['id'],
            rep['name'],
            cust['area_name'] or "General",
            float(cust['discount_tier']),
            valid_payment_mode,
            summary['subtotal'],
            summary['discount_amount'],
            summary['grand_total'],
            now.strftime('%Y-%m-%d %H:%M:%S')
        ))
        invoice_id = cursor.lastrowid

        # Insert line items & deduct stock
        items_inserted = []
        for item in cart_items:
            product_id = item['product_id']
            qty = int(item['quantity'])
            
            # Check stock
            cursor.execute("SELECT name, stock, mrp, has_tp FROM products WHERE id = ?;", (product_id,))
            prod = cursor.fetchone()
            if not prod:
                raise ValueError(f"Product ID {product_id} not found.")
            
            if prod['stock'] < qty:
                raise ValueError(f"Insufficient stock for '{prod['name']}'. Available: {prod['stock']}, Requested: {qty}.")

            mrp = float(item.get('mrp', prod['mrp']))
            has_tp = bool(item.get('has_tp', bool(prod['has_tp'])))
            tp = calculate_tp(mrp, has_tp=has_tp)

            # Customer discount tier is default, but item-level discount takes precedence if specified
            disc_pct = float(item.get('discount_percent', cust['discount_tier']))
            final_rate = calculate_final_rate(tp, disc_pct)
            total_price = calculate_line_total(final_rate, qty)

            cursor.execute("""
                INSERT INTO invoice_items (
                    invoice_id, product_id, product_name, mrp, has_tp, tp,
                    discount_percent, final_rate, quantity, total_price
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                invoice_id, product_id, prod['name'], mrp, 1 if has_tp else 0, tp,
                disc_pct, final_rate, qty, total_price
            ))

            # Deduct stock
            cursor.execute("UPDATE products SET stock = stock - ? WHERE id = ?;", (qty, product_id))

            items_inserted.append({
                'product_id': product_id,
                'product_name': prod['name'],
                'mrp': mrp,
                'has_tp': has_tp,
                'tp': tp,
                'discount_percent': disc_pct,
                'final_rate': final_rate,
                'quantity': qty,
                'total_price': total_price
            })

        # Update sequence for next invoice (increment 1 -> 2 -> 3)
        cursor.execute("UPDATE app_settings SET value = ? WHERE key = 'next_invoice_seq';", (str(seq_num + 1),))

        conn.commit()

        return {
            'id': invoice_id,
            'invoice_number': invoice_number,
            'seq_num': seq_num,
            'customer_id': cust['id'],
            'customer_name': cust['name'],
            'customer_phone': cust['phone'],
            'customer_address': cust['address'],
            'sales_rep_id': rep['id'],
            'sales_rep_name': rep['name'],
            'area_name': cust['area_name'] or "General",
            'discount_tier': cust['discount_tier'],
            'payment_mode': valid_payment_mode,
            'subtotal': summary['subtotal'],
            'discount_amount': summary['discount_amount'],
            'grand_total': summary['grand_total'],
            'created_at': now.strftime('%Y-%m-%d %H:%M:%S'),
            'items': items_inserted
        }

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def get_invoices(start_date: Optional[str] = None, end_date: Optional[str] = None, search_query: str = "", payment_mode: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM invoices WHERE 1=1"
    params = []

    if start_date:
        query += " AND DATE(created_at) >= DATE(?)"
        params.append(start_date)
    if end_date:
        query += " AND DATE(created_at) <= DATE(?)"
        params.append(end_date)
    if search_query.strip():
        term = f"%{search_query.strip()}%"
        query += " AND (invoice_number LIKE ? OR customer_name LIKE ? OR sales_rep_name LIKE ?)"
        params.extend([term, term, term])
    if payment_mode and payment_mode != "All":
        query += " AND payment_mode = ?"
        params.append(payment_mode)

    query += " ORDER BY id DESC;"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        if not d.get('payment_mode'):
            d['payment_mode'] = 'Cash'
        result.append(d)
    return result


def get_invoice_by_id(invoice_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM invoices WHERE id = ?;", (invoice_id,))
    inv_row = cursor.fetchone()
    if not inv_row:
        conn.close()
        return None

    inv = dict(inv_row)
    if not inv.get('payment_mode'):
        inv['payment_mode'] = 'Cash'

    # Fetch customer extra info
    cursor.execute("SELECT phone, address FROM customers WHERE id = ?;", (inv['customer_id'],))
    cust_row = cursor.fetchone()
    if cust_row:
        inv['customer_phone'] = cust_row['phone']
        inv['customer_address'] = cust_row['address']
    else:
        inv['customer_phone'] = ""
        inv['customer_address'] = ""

    # Fetch items
    cursor.execute("SELECT * FROM invoice_items WHERE invoice_id = ? ORDER BY id ASC;", (invoice_id,))
    items_rows = cursor.fetchall()
    conn.close()

    items = []
    for i in items_rows:
        item_d = dict(i)
        item_d['has_tp'] = bool(item_d.get('has_tp', 1))
        items.append(item_d)

    inv['items'] = items
    return inv


# ==========================================
# BUSINESS INTELLIGENCE & REPORTING DAO
# ==========================================

def get_dashboard_summary() -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()

    today_str = datetime.now().strftime('%Y-%m-%d')

    # Today's Sales & Invoices Count (Overall + Cash + Credit)
    cursor.execute("""
        SELECT 
            COUNT(*) as count, 
            COALESCE(SUM(grand_total), 0.0) as total_revenue,
            COALESCE(SUM(CASE WHEN payment_mode = 'Cash' THEN grand_total ELSE 0 END), 0.0) as cash_revenue,
            COALESCE(SUM(CASE WHEN payment_mode = 'Credit' THEN grand_total ELSE 0 END), 0.0) as credit_revenue,
            COUNT(CASE WHEN payment_mode = 'Cash' THEN 1 END) as cash_count,
            COUNT(CASE WHEN payment_mode = 'Credit' THEN 1 END) as credit_count
        FROM invoices
        WHERE DATE(created_at) = DATE(?);
    """, (today_str,))
    today_row = cursor.fetchone()

    # Active Products Count
    cursor.execute("SELECT COUNT(*) as count FROM products;")
    prod_row = cursor.fetchone()

    # Low Stock Count
    cursor.execute("SELECT COUNT(*) as count FROM products WHERE stock <= reorder_level;")
    low_stock_row = cursor.fetchone()

    # Recent 5 Invoices
    cursor.execute("SELECT * FROM invoices ORDER BY id DESC LIMIT 5;")
    recent_invs = []
    for r in cursor.fetchall():
        d = dict(r)
        if not d.get('payment_mode'):
            d['payment_mode'] = 'Cash'
        recent_invs.append(d)

    conn.close()

    return {
        'today_revenue': float(today_row['total_revenue']),
        'today_cash_revenue': float(today_row['cash_revenue']),
        'today_credit_revenue': float(today_row['credit_revenue']),
        'today_invoices_count': int(today_row['count']),
        'today_cash_count': int(today_row['cash_count']),
        'today_credit_count': int(today_row['credit_count']),
        'total_products_count': int(prod_row['count']),
        'low_stock_count': int(low_stock_row['count']),
        'recent_invoices': recent_invs
    }


def get_sales_by_sales_rep(start_date: str, end_date: str, payment_mode: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            sales_rep_name,
            COUNT(id) AS total_invoices,
            COALESCE(SUM(grand_total), 0.0) AS total_revenue,
            COALESCE(SUM(CASE WHEN payment_mode = 'Cash' THEN grand_total ELSE 0 END), 0.0) AS cash_revenue,
            COALESCE(SUM(CASE WHEN payment_mode = 'Credit' THEN grand_total ELSE 0 END), 0.0) AS credit_revenue
        FROM invoices
        WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)
    """
    params = [start_date, end_date]
    if payment_mode and payment_mode != "All":
        query += " AND payment_mode = ?"
        params.append(payment_mode)
    query += " GROUP BY sales_rep_name ORDER BY total_revenue DESC;"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_sales_by_area(start_date: str, end_date: str, payment_mode: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            COALESCE(NULLIF(area_name, ''), 'Unassigned') AS area_name,
            COUNT(id) AS total_invoices,
            COALESCE(SUM(grand_total), 0.0) AS total_revenue,
            COALESCE(SUM(CASE WHEN payment_mode = 'Cash' THEN grand_total ELSE 0 END), 0.0) AS cash_revenue,
            COALESCE(SUM(CASE WHEN payment_mode = 'Credit' THEN grand_total ELSE 0 END), 0.0) AS credit_revenue
        FROM invoices
        WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)
    """
    params = [start_date, end_date]
    if payment_mode and payment_mode != "All":
        query += " AND payment_mode = ?"
        params.append(payment_mode)
    query += " GROUP BY area_name ORDER BY total_revenue DESC;"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_sales_by_product(start_date: str, end_date: str, payment_mode: Optional[str] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT 
            ii.product_name,
            SUM(ii.quantity) AS total_quantity_sold,
            COALESCE(SUM(ii.total_price), 0.0) AS total_revenue
        FROM invoice_items ii
        JOIN invoices i ON ii.invoice_id = i.id
        WHERE DATE(i.created_at) BETWEEN DATE(?) AND DATE(?)
    """
    params = [start_date, end_date]
    if payment_mode and payment_mode != "All":
        query += " AND i.payment_mode = ?"
        params.append(payment_mode)
    query += " GROUP BY ii.product_name ORDER BY total_revenue DESC;"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_sales_by_payment_mode(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            COALESCE(NULLIF(payment_mode, ''), 'Cash') AS payment_mode,
            COUNT(id) AS total_invoices,
            COALESCE(SUM(subtotal), 0.0) AS total_subtotal,
            COALESCE(SUM(discount_amount), 0.0) AS total_discount,
            COALESCE(SUM(grand_total), 0.0) AS total_revenue
        FROM invoices
        WHERE DATE(created_at) BETWEEN DATE(?) AND DATE(?)
        GROUP BY payment_mode
        ORDER BY total_revenue DESC;
    """, (start_date, end_date))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]
