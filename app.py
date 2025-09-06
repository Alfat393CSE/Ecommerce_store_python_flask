from flask import Flask, render_template, session, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "mysecretkey"  # Needed for session

# Dummy product data
products = [
    {"id": 1, "name": "Smartphone", "price": 250, "img": "images/phone.jpg"},
    {"id": 2, "name": "Headphones", "price": 50, "img": "images/headphones.jpg"},
    {"id": 3, "name": "Smartwatch", "price": 120, "img": "images/watch.jpg"},
]

# In-memory user store (use DB in real apps)
users = {}

@app.route("/")
def home():
    return render_template("home.html", products=products, user=session.get("user"))

@app.route("/product/<int:pid>")
def product(pid):
    product = next((p for p in products if p["id"] == pid), None)
    return render_template("product.html", product=product, user=session.get("user"))

@app.route("/add_to_cart/<int:pid>")
def add_to_cart(pid):
    cart = session.get("cart", {})
    cart[pid] = cart.get(pid, 0) + 1
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    cart = session.get("cart", {})
    cart_items = []
    total = 0
    for pid, qty in cart.items():
        product = next((p for p in products if p["id"] == pid), None)
        if product:
            subtotal = product["price"] * qty
            total += subtotal
            cart_items.append({"product": product, "qty": qty, "subtotal": subtotal})
    return render_template("cart.html", cart_items=cart_items, total=total, user=session.get("user"))

@app.route("/remove_from_cart/<int:pid>")
def remove_from_cart(pid):
    cart = session.get("cart", {})
    cart.pop(pid, None)
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/checkout")
def checkout():
    if "user" not in session:
        flash("You must log in to checkout!", "error")
        return redirect(url_for("login"))

    session.pop("cart", None)  # clear cart after checkout
    return render_template("checkout.html", user=session.get("user"))

# ---------- User Authentication ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users:
            flash("Username already exists!", "error")
        else:
            users[username] = generate_password_hash(password)
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for("login"))
    return render_template("signup.html", user=session.get("user"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and check_password_hash(users[username], password):
            session["user"] = username
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password!", "error")
    return render_template("login.html", user=session.get("user"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully!", "success")
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
