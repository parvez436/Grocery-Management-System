PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    unit TEXT NOT NULL DEFAULT 'kg',
    price REAL NOT NULL CHECK(price >= 0),
    stock REAL NOT NULL CHECK(stock >= 0)
);

CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    discount_percent REAL NOT NULL DEFAULT 0 CHECK(discount_percent >= 0 AND discount_percent <= 100),
    subtotal REAL NOT NULL DEFAULT 0 CHECK(subtotal >= 0),
    discount_amount REAL NOT NULL DEFAULT 0 CHECK(discount_amount >= 0),
    total REAL NOT NULL DEFAULT 0 CHECK(total >= 0),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bill_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity REAL NOT NULL CHECK(quantity > 0),
    unit_price REAL NOT NULL CHECK(unit_price >= 0),
    line_total REAL NOT NULL CHECK(line_total >= 0),
    FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS cart (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    quantity REAL NOT NULL CHECK(quantity > 0),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);