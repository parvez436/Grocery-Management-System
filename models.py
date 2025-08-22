import sqlite3
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime

DB = Path(__file__).with_name('grocery.db')

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    if DB.exists():
        return
    schema = Path(__file__).with_name('schema.sql').read_text(encoding='utf-8')
    with get_conn() as conn:
        conn.executescript(schema)
    # sample data
    with get_conn() as conn:
        conn.execute("INSERT INTO products(name, unit, price, stock) VALUES(?,?,?,?);", ('Rice','kg',50.0,20.0))
        conn.execute("INSERT INTO products(name, unit, price, stock) VALUES(?,?,?,?);", ('Sugar','kg',40.0,15.0))
        conn.execute("INSERT INTO products(name, unit, price, stock) VALUES(?,?,?,?);", ('Tea Powder','kg',200.0,5.0))
        conn.execute("INSERT INTO products(name, unit, price, stock) VALUES(?,?,?,?);", ('Eggs','piece',6.0,100))
        # cart empty initially

def get_db_path():
    return str(DB)

def get_all_products():
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM products ORDER BY name;")
        return [dict(r) for r in cur.fetchall()]

def add_product(name, unit, price, stock):
    with get_conn() as conn:
        conn.execute("INSERT INTO products(name, unit, price, stock) VALUES(?,?,?,?);", (name,unit,float(price),float(stock)))

def get_product(pid):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM products WHERE id=?;", (int(pid),))
        r = cur.fetchone()
        return dict(r) if r else None

# cart operations
def get_cart():
    with get_conn() as conn:
        cur = conn.execute("SELECT c.id, c.product_id, c.quantity, p.name, p.unit, p.price FROM cart c JOIN products p ON p.id = c.product_id;")
        return [dict(r) for r in cur.fetchall()]

def add_to_cart(product_id, quantity):
    with get_conn() as conn:
        cur = conn.execute("SELECT stock FROM products WHERE id=?;", (int(product_id),))
        r = cur.fetchone()
        if not r:
            raise ValueError('Product not found')
        if r['stock'] < float(quantity):
            raise ValueError('Insufficient stock')
        conn.execute("INSERT INTO cart(product_id, quantity) VALUES(?,?);", (int(product_id), float(quantity)))

def remove_from_cart(cid):
    with get_conn() as conn:
        conn.execute("DELETE FROM cart WHERE id=?;", (int(cid),))

def clear_cart():
    with get_conn() as conn:
        conn.execute("DELETE FROM cart;")

# billing
def create_bill(customer_name, discount_percent, items):
    discount_percent = float(discount_percent or 0)
    if not items:
        raise ValueError('No items to bill')
    with get_conn() as conn:
        line_items = []
        subtotal = 0.0
        for it in items:
            pid = int(it['product_id'])
            qty = float(it['quantity'])
            cur = conn.execute("SELECT id, name, unit, price, stock FROM products WHERE id=?;", (pid,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f'Product id {pid} not found')
            if row['stock'] < qty:
                raise ValueError(f'Insufficient stock for {row["name"]}')
            unit_price = float(row['price'])
            line_total = unit_price * qty
            subtotal += line_total
            line_items.append({'product_id': pid, 'quantity': qty, 'unit_price': unit_price, 'line_total': line_total})
        discount_amount = round(subtotal * (discount_percent/100.0),2)
        total = round(subtotal - discount_amount,2)
        cur = conn.execute("INSERT INTO bills(customer_name, discount_percent, subtotal, discount_amount, total, created_at) VALUES(?,?,?,?,?,?);", (customer_name or None, discount_percent, round(subtotal,2), discount_amount, total, datetime.now().isoformat(timespec='seconds')))
        bill_id = cur.lastrowid
        for li in line_items:
            conn.execute("INSERT INTO bill_items(bill_id, product_id, quantity, unit_price, line_total) VALUES(?,?,?,?,?);", (bill_id, li['product_id'], li['quantity'], li['unit_price'], round(li['line_total'],2)))
            conn.execute("UPDATE products SET stock = stock - ? WHERE id=?;", (li['quantity'], li['product_id']))
        return bill_id

def get_bill(bill_id):
    with get_conn() as conn:
        cur = conn.execute("SELECT * FROM bills WHERE id=?;", (int(bill_id),))
        b = cur.fetchone()
        if not b:
            return None, []
        bill = dict(b)
        cur = conn.execute("SELECT bi.*, p.name, p.unit FROM bill_items bi JOIN products p ON p.id = bi.product_id WHERE bi.bill_id=?;", (int(bill_id),))
        items = [dict(r) for r in cur.fetchall()]
        return bill, items