from flask import Flask, render_template, request, redirect, url_for, session
from database import init_db, add_product, get_products, update_stock, get_product_by_id
from database import update_product, delete_product
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = "secret123"

# Initialize DB
init_db()

@app.route("/")
def home():
    return render_template("home.html")

# ------------------- Add Product -------------------
@app.route("/add_product", methods=["GET", "POST"])
def add_product_route():
    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        stock = float(request.form["stock"])
        add_product(name, price, stock)
        return redirect(url_for("view_products"))
    return render_template("add_product.html")

# ------------------- Update Product -------------------
@app.route("/update_product/<int:product_id>", methods=["GET", "POST"])
def update_product_route(product_id):
    product = get_product_by_id(product_id)
    if not product:
        return "Product not found", 404

    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        stock = float(request.form["stock"])
        update_product(product_id, name, price, stock)
        return redirect(url_for("view_products"))

    return render_template("update_product.html", product=product)

# ------------------- Delete Product -------------------
@app.route("/delete_product/<int:product_id>", methods=["POST"])
def delete_product_route(product_id):
    delete_product(product_id)
    return redirect(url_for("view_products"))

# ------------------- View Products -------------------
@app.route("/view_products")
def view_products():
    products = get_products()
    return render_template("view_products.html", products=products)

# ------------------- Add to Cart -------------------
@app.route("/add_to_cart", methods=["GET", "POST"])
def add_to_cart():
    if "cart" not in session:
        session["cart"] = []

    if request.method == "POST":
        product_id = int(request.form["product_id"])
        qty = float(request.form["quantity"])
        product = get_product_by_id(product_id)

        if product and qty <= product[3]:  # stock check
            session["cart"].append({
                "id": product[0],
                "name": product[1],
                "price": product[2],
                "qty": qty,
                "total": qty * product[2]
            })
            update_stock(product_id, product[3] - qty)

        session.modified = True
        return redirect(url_for("view_bill"))

    products = get_products()
    return render_template("add_to_cart.html", products=products)

# ------------------- View Bill -------------------
@app.route("/bill", methods=["GET", "POST"])
def view_bill():
    # Generate unique invoice number (combination of date and random number)
    invoice_number = int(datetime.now().strftime("%Y%m%d")) * 100 + random.randint(1, 99)
    
    # Get current date and time
    current_date = datetime.now()
    
    # Calculate cart totals
    cart = session.get("cart", [])
    valid_cart = []
    total = 0

    # Only count cart items that still exist in DB
    for item in cart:
        product = get_product_by_id(item["id"])
        if product:
            valid_cart.append(item)
            total += item["total"]
    
    # Handle discount submission
    discount_percentage = 0
    discount_amount = 0
    
    # Apply automatic 10% discount for orders over 500
    if total > 500:
        discount_percentage = 10
        discount_amount = total * 0.1
    
    # Also check for manual discount input
    if request.method == "POST" and "discount" in request.form:
        try:
            discount_percentage = float(request.form["discount"])
            discount_amount = total * (discount_percentage / 100)
        except ValueError:
            pass  # Handle invalid input if needed
    
    grand_total = total - discount_amount
    
    return render_template("view_bill.html",
                         cart=valid_cart,
                         total=total,
                         discount_percentage=discount_percentage,
                         discount_amount=discount_amount,
                         grand_total=grand_total,
                         invoice_number=invoice_number,
                         current_date=current_date)

if __name__ == "__main__":
    app.run(debug=True)