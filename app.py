from flask import Flask, render_template, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "mysecretkey"  # Needed for session

# Dummy product data
products = [
    {"id": 1, "name": "Smartphone", "price": 250, "img": "images/phone.jpg"},
    {"id": 2, "name": "Headphones", "price": 50, "img": "images/headphones.jpg"},
    {"id": 3, "name": "Smartwatch", "price": 120, "img": "images/watch.jpg"},
]

@app.route("/")
def home():
    return render_template("home.html", products=products)

@app.route("/product/<int:pid>")
def product(pid):
    product = next((p for p in products if p["id"] == pid), None)
    return render_template("product.html", product=product)

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
    return render_template("cart.html", cart_items=cart_items, total=total)

@app.route("/remove_from_cart/<int:pid>")
def remove_from_cart(pid):
    cart = session.get("cart", {})
    if str(pid) in cart:
        cart.pop(str(pid))
    else:
        cart.pop(pid, None)
    session["cart"] = cart
    return redirect(url_for("cart"))

@app.route("/checkout")
def checkout():
    session.pop("cart", None)  # clear cart after checkout
    return render_template("checkout.html")

if __name__ == "__main__":
    app.run(debug=True)
