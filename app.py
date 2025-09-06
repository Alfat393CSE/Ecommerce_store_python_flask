from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "mysecretkey"

# Database setup (SQLite file)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ecommerce.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# ----------------- Models -----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    img = db.Column(db.String(200), nullable=False)

# ----------------- Routes -----------------
@app.route("/")
def home():
    products = Product.query.all()
    return render_template("home.html", products=products, user=session.get("user"))

@app.route("/product/<int:pid>")
def product(pid):
    product = Product.query.get(pid)
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
    cart_items, total = [], 0
    for pid, qty in cart.items():
        product = Product.query.get(pid)
        if product:
            subtotal = product.price * qty
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

    session.pop("cart", None)  # clear cart
    return render_template("checkout.html", user=session.get("user"))

# ---------- Authentication ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "error")
        else:
            hashed_pw = generate_password_hash(password)
            new_user = User(username=username, password=hashed_pw)
            db.session.add(new_user)
            db.session.commit()
            flash("Signup successful! Please log in.", "success")
            return redirect(url_for("login"))

    return render_template("signup.html", user=session.get("user"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
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

# ----------------- Initialize DB -----------------
def create_tables():
    db.create_all()
    if not Product.query.first():  # Add some products if DB is empty
        sample_products = [
            Product(name="Smartphone", price=250, img="images/phone.jpg"),
            Product(name="Headphones", price=50, img="images/headphones.jpg"),
            Product(name="Smartwatch", price=120, img="images/watch.jpg"),
        ]
        db.session.add_all(sample_products)
        db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        create_tables()  # run once when app starts
    app.run(debug=True)
