import sqlite3

def init_db():
    conn = sqlite3.connect("grocery.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            stock REAL
        )
    """)
    conn.commit()
    conn.close()

def add_product(name, price, stock):
    conn = sqlite3.connect("grocery.db")
    cur = conn.cursor()
    cur.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
    conn.commit()
    conn.close()

def get_products():
    conn = sqlite3.connect("grocery.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    conn.close()
    return products

def get_product_by_id(product_id):
    conn = sqlite3.connect("grocery.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM products WHERE id=?", (product_id,))
    product = cur.fetchone()
    conn.close()
    return product

def update_stock(product_id, new_stock):
    """ Update only stock after purchase """
    conn = sqlite3.connect("grocery.db")
    cur = conn.cursor()
    cur.execute("UPDATE products SET stock=? WHERE id=?", (new_stock, product_id))
    conn.commit()
    conn.close()

def update_product(product_id, name, price, stock):
    """ Edit/Update product details """
    conn = sqlite3.connect("grocery.db")
    cur = conn.cursor()
    cur.execute("UPDATE products SET name=?, price=?, stock=? WHERE id=?", (name, price, stock, product_id))
    conn.commit()
    conn.close()

def delete_product(product_id):
    """ Delete product by ID """
    conn = sqlite3.connect("grocery.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=?", (product_id,))
    conn.commit()
    conn.close()
