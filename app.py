"""Local Farmer Market Information System - Flask + SQLite

Modules
  1. Registration & Login        5. Local Market Price Information
  2. Farmer Product Management   6. Contact / Inquiry System
  3. Browse, Search & Filter     7. Admin Panel
  4. Price Comparison
"""
import os
import sqlite3
from datetime import date, timedelta
from functools import wraps

from flask import (Flask, g, render_template, request, redirect,
                   url_for, flash, session, abort)
from werkzeug.security import generate_password_hash, check_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "market.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-before-deploying")

CATEGORIES = ["Vegetables", "Fruits", "Grains", "Pulses", "Dairy", "Spices", "Flowers", "Other"]
UNITS = ["kg", "quintal", "dozen", "litre", "piece"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, phone TEXT UNIQUE NOT NULL, location TEXT NOT NULL,
  password TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('farmer','customer','admin')),
  active INTEGER DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  farmer_id INTEGER NOT NULL REFERENCES users(id),
  name TEXT NOT NULL, category TEXT, price REAL NOT NULL, unit TEXT DEFAULT 'kg',
  quantity INTEGER NOT NULL, description TEXT, available INTEGER DEFAULT 1,
  updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS market_prices (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  crop TEXT NOT NULL, market TEXT NOT NULL, price_per_kg REAL NOT NULL, price_date TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS inquiries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL REFERENCES products(id),
  customer_id INTEGER NOT NULL REFERENCES users(id),
  message TEXT NOT NULL, reply TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
"""

# ---------------------------------------------------------------- database
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db:
        db.close()

def query(sql, args=(), one=False):
    rows = get_db().execute(sql, args).fetchall()
    return (rows[0] if rows else None) if one else rows

def execute(sql, args=()):
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid

def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    if query("SELECT 1 FROM users LIMIT 1", one=True):
        return
    pw = generate_password_hash
    users = [("Admin", "9999999999", "Mysuru", pw("admin123"), "admin"),
             ("Ramesh Gowda", "9876500001", "Nanjangud", pw("farmer123"), "farmer"),
             ("Lakshmi Devi", "9876500002", "Hunsur", pw("farmer123"), "farmer"),
             ("Mahadevappa", "9876500003", "T. Narasipura", pw("farmer123"), "farmer"),
             ("Anita Rao", "9876500004", "Mysuru", pw("customer123"), "customer")]
    db.executemany("INSERT INTO users(name,phone,location,password,role) VALUES(?,?,?,?,?)", users)
    products = [(2, "Tomato", "Vegetables", 24, "kg", 300, "Fresh red tomatoes, picked this morning."),
                (3, "Tomato", "Vegetables", 22, "kg", 150, "Country variety, good for sambar."),
                (4, "Tomato", "Vegetables", 26, "kg", 500, "Hybrid, firm and uniform."),
                (2, "Onion", "Vegetables", 30, "kg", 800, "Dry onions, well cured."),
                (3, "Banana (Nanjangud Rasabale)", "Fruits", 60, "dozen", 120, "Famous local rasabale bananas."),
                (4, "Ragi", "Grains", 3800, "quintal", 40, "Stone-cleaned finger millet."),
                (3, "Jasmine", "Flowers", 400, "kg", 25, "Mysuru mallige, harvested at dawn."),
                (2, "Cow Milk", "Dairy", 48, "litre", 60, "Raw milk, delivered daily.")]
    db.executemany("INSERT INTO products(farmer_id,name,category,price,unit,quantity,description)"
                   " VALUES(?,?,?,?,?,?,?)", products)
    today = date.today()
    prices = [("Tomato", "Devaraja Market, Mysuru", 28, 0), ("Tomato", "Bandipalya APMC", 25, 0),
              ("Onion", "Devaraja Market, Mysuru", 33, 0), ("Onion", "Bandipalya APMC", 31, 0),
              ("Potato", "Devaraja Market, Mysuru", 35, 0), ("Ragi", "Bandipalya APMC", 38, 0),
              ("Banana (Nanjangud Rasabale)", "Devaraja Market, Mysuru", 5, 0),
              ("Tomato", "Devaraja Market, Mysuru", 30, 1), ("Onion", "Devaraja Market, Mysuru", 34, 1)]
    db.executemany("INSERT INTO market_prices(crop,market,price_per_kg,price_date) VALUES(?,?,?,?)",
                   [(c, m, p, (today - timedelta(days=d)).isoformat()) for c, m, p, d in prices])
    db.execute("INSERT INTO inquiries(product_id,customer_id,message) VALUES(1,5,'Can you deliver 20 kg to Mysuru this weekend?')")
    db.commit()

# -------------------------------------------------------------------- auth
@app.before_request
def load_user():
    uid = session.get("uid")
    g.user = query("SELECT * FROM users WHERE id=? AND active=1", (uid,), one=True) if uid else None

def login_required(*roles):
    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            if not g.user:
                flash("Please log in to continue.", "error")
                return redirect(url_for("login", next=request.path))
            if roles and g.user["role"] not in roles:
                abort(403)
            return fn(*a, **kw)
        return wrapper
    return deco

@app.context_processor
def inject():
    return {"CATEGORIES": CATEGORIES, "UNITS": UNITS}

# ---------------------------------------- Module 1: registration & login
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        f = request.form
        name, phone = f.get("name", "").strip(), f.get("phone", "").strip()
        location, role, pw = f.get("location", "").strip(), f.get("role"), f.get("password", "")
        if not name or not location:
            err = "Name and location are required."
        elif not (phone.isdigit() and len(phone) == 10):
            err = "Enter a 10-digit phone number."
        elif len(pw) < 6:
            err = "Password must be at least 6 characters."
        elif role not in ("farmer", "customer"):
            err = "Choose whether you are a farmer or a customer."
        elif query("SELECT 1 FROM users WHERE phone=?", (phone,), one=True):
            err = "This phone number is already registered. Log in instead."
        else:
            err = None
        if err:
            flash(err, "error")
        else:
            execute("INSERT INTO users(name,phone,location,password,role) VALUES(?,?,?,?,?)",
                    (name, phone, location, generate_password_hash(pw), role))
            flash("Account created. You can log in now.", "ok")
            return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = query("SELECT * FROM users WHERE phone=?", (request.form.get("phone", "").strip(),), one=True)
        if user and check_password_hash(user["password"], request.form.get("password", "")):
            if not user["active"]:
                flash("This account has been deactivated. Contact the admin.", "error")
            else:
                session.clear()
                session["uid"] = user["id"]
                nxt = request.args.get("next", "")
                return redirect(nxt if nxt.startswith("/") else url_for("dashboard"))
        else:
            flash("Phone number or password is incorrect.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "ok")
    return redirect(url_for("index"))

# ------------------------------------ Module 3: browse, search & filter
SORTS = {"new": "p.updated_at DESC", "low": "p.price ASC", "high": "p.price DESC", "name": "p.name ASC"}

@app.route("/")
def index():
    q, cat = request.args.get("q", "").strip(), request.args.get("category", "")
    loc, sort = request.args.get("location", "").strip(), request.args.get("sort", "new")
    sql = ("SELECT p.*, u.name AS farmer, u.location FROM products p JOIN users u ON u.id=p.farmer_id "
           "WHERE p.available=1 AND p.quantity>0 AND u.active=1")
    args = []
    if q:
        sql += " AND p.name LIKE ?"; args.append(f"%{q}%")
    if cat in CATEGORIES:
        sql += " AND p.category=?"; args.append(cat)
    if loc:
        sql += " AND u.location LIKE ?"; args.append(f"%{loc}%")
    sql += " ORDER BY " + SORTS.get(sort, SORTS["new"])
    board = query("SELECT crop, market, price_per_kg FROM market_prices "
                  "WHERE price_date=(SELECT MAX(price_date) FROM market_prices) ORDER BY crop LIMIT 6")
    return render_template("index.html", products=query(sql, args), board=board,
                           q=q, cat=cat, loc=loc, sort=sort)

@app.route("/product/<int:pid>")
def product(pid):
    p = query("SELECT p.*, u.name AS farmer, u.phone, u.location FROM products p "
              "JOIN users u ON u.id=p.farmer_id WHERE p.id=?", (pid,), one=True) or abort(404)
    mkt = query("SELECT AVG(price_per_kg) AS avg FROM market_prices WHERE lower(crop)=lower(?)", (p["name"],), one=True)
    return render_template("product.html", p=p, market_avg=mkt["avg"])

# ------------------------------------------- Module 4: price comparison
@app.route("/compare")
def compare():
    crops = query("SELECT DISTINCT name FROM products WHERE available=1 ORDER BY name")
    crop = request.args.get("crop", "").strip()
    rows, mkt = [], None
    if crop:
        rows = query("SELECT p.*, u.name AS farmer, u.location FROM products p JOIN users u ON u.id=p.farmer_id "
                     "WHERE lower(p.name)=lower(?) AND p.available=1 AND p.quantity>0 AND u.active=1 "
                     "ORDER BY p.price", (crop,))
        mkt = query("SELECT AVG(price_per_kg) AS avg, MIN(price_per_kg) AS lo, MAX(price_per_kg) AS hi "
                    "FROM market_prices WHERE lower(crop)=lower(?)", (crop,), one=True)
    return render_template("compare.html", crops=crops, crop=crop, rows=rows, mkt=mkt)

# ------------------------------- Module 5: local market price information
@app.route("/prices")
def prices():
    crop = request.args.get("crop", "").strip()
    sql, args = "SELECT * FROM market_prices", []
    if crop:
        sql += " WHERE lower(crop)=lower(?)"; args.append(crop)
    rows = query(sql + " ORDER BY price_date DESC, crop", args)
    crops = query("SELECT DISTINCT crop FROM market_prices ORDER BY crop")
    return render_template("prices.html", rows=rows, crops=crops, crop=crop)

# ------------------------------------ Module 2: farmer product management
def read_product_form():
    f = request.form
    name = f.get("name", "").strip()
    try:
        price, qty = float(f.get("price", "")), int(f.get("quantity", ""))
    except ValueError:
        return None, "Price and quantity must be numbers."
    if not name:
        return None, "Product name is required."
    if price <= 0 or qty < 0:
        return None, "Price must be above 0 and quantity cannot be negative."
    cat = f.get("category") if f.get("category") in CATEGORIES else "Other"
    unit = f.get("unit") if f.get("unit") in UNITS else "kg"
    return (name, cat, price, unit, qty, f.get("description", "").strip(), 1 if f.get("available") else 0), None

@app.route("/product/new", methods=["GET", "POST"])
@login_required("farmer")
def product_new():
    if request.method == "POST":
        data, err = read_product_form()
        if err:
            flash(err, "error")
        else:
            execute("INSERT INTO products(name,category,price,unit,quantity,description,available,farmer_id)"
                    " VALUES(?,?,?,?,?,?,?,?)", data + (g.user["id"],))
            flash("Product listed.", "ok")
            return redirect(url_for("dashboard"))
    return render_template("product_form.html", p=None)

def own_product(pid):
    p = query("SELECT * FROM products WHERE id=?", (pid,), one=True) or abort(404)
    if p["farmer_id"] != g.user["id"]:
        abort(403)
    return p

@app.route("/product/<int:pid>/edit", methods=["GET", "POST"])
@login_required("farmer")
def product_edit(pid):
    p = own_product(pid)
    if request.method == "POST":
        data, err = read_product_form()
        if err:
            flash(err, "error")
        else:
            execute("UPDATE products SET name=?,category=?,price=?,unit=?,quantity=?,description=?,available=?,"
                    "updated_at=CURRENT_TIMESTAMP WHERE id=?", data + (pid,))
            flash("Product updated.", "ok")
            return redirect(url_for("dashboard"))
    return render_template("product_form.html", p=p)

@app.route("/product/<int:pid>/delete", methods=["POST"])
@login_required("farmer")
def product_delete(pid):
    own_product(pid)
    execute("DELETE FROM inquiries WHERE product_id=?", (pid,))
    execute("DELETE FROM products WHERE id=?", (pid,))
    flash("Product removed.", "ok")
    return redirect(url_for("dashboard"))

# ----------------------------------------- Module 6: contact / inquiries
@app.route("/product/<int:pid>/inquire", methods=["POST"])
@login_required("customer")
def inquire(pid):
    query("SELECT 1 FROM products WHERE id=?", (pid,), one=True) or abort(404)
    msg = request.form.get("message", "").strip()
    if len(msg) < 5:
        flash("Write a short message for the farmer.", "error")
    else:
        execute("INSERT INTO inquiries(product_id,customer_id,message) VALUES(?,?,?)", (pid, g.user["id"], msg))
        flash("Message sent. The farmer's reply will appear in your dashboard.", "ok")
    return redirect(url_for("product", pid=pid))

@app.route("/inquiry/<int:iid>/reply", methods=["POST"])
@login_required("farmer")
def reply(iid):
    query("SELECT i.id FROM inquiries i JOIN products p ON p.id=i.product_id "
          "WHERE i.id=? AND p.farmer_id=?", (iid, g.user["id"]), one=True) or abort(403)
    execute("UPDATE inquiries SET reply=? WHERE id=?", (request.form.get("reply", "").strip(), iid))
    flash("Reply sent.", "ok")
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
@login_required()
def dashboard():
    role, uid = g.user["role"], g.user["id"]
    if role == "admin":
        return redirect(url_for("admin"))
    if role == "farmer":
        prods = query("SELECT * FROM products WHERE farmer_id=? ORDER BY updated_at DESC", (uid,))
        inq = query("SELECT i.*, p.name AS product, u.name AS customer, u.phone FROM inquiries i "
                    "JOIN products p ON p.id=i.product_id JOIN users u ON u.id=i.customer_id "
                    "WHERE p.farmer_id=? ORDER BY i.created_at DESC", (uid,))
        return render_template("dashboard_farmer.html", products=prods, inquiries=inq)
    inq = query("SELECT i.*, p.name AS product, p.id AS pid, u.name AS farmer, u.phone FROM inquiries i "
                "JOIN products p ON p.id=i.product_id JOIN users u ON u.id=p.farmer_id "
                "WHERE i.customer_id=? ORDER BY i.created_at DESC", (uid,))
    return render_template("dashboard_customer.html", inquiries=inq)

# ------------------------------------------------- Module 7: admin panel
@app.route("/admin")
@login_required("admin")
def admin():
    stats = {k: query(f"SELECT COUNT(*) c FROM {t}" + (f" WHERE {w}" if w else ""), one=True)["c"]
             for k, t, w in [("farmers", "users", "role='farmer'"), ("customers", "users", "role='customer'"),
                             ("products", "products", ""), ("inquiries", "inquiries", "")]}
    return render_template("admin.html", stats=stats,
                           users=query("SELECT * FROM users WHERE role!='admin' ORDER BY created_at DESC"),
                           prices=query("SELECT * FROM market_prices ORDER BY price_date DESC, id DESC LIMIT 30"),
                           today=date.today().isoformat())

@app.route("/admin/user/<int:uid>/toggle", methods=["POST"])
@login_required("admin")
def admin_toggle(uid):
    execute("UPDATE users SET active=1-active WHERE id=? AND role!='admin'", (uid,))
    flash("User status changed.", "ok")
    return redirect(url_for("admin"))

@app.route("/admin/price", methods=["POST"])
@login_required("admin")
def admin_price_add():
    f = request.form
    try:
        price = float(f.get("price_per_kg", ""))
        assert f.get("crop", "").strip() and f.get("market", "").strip() and price > 0
    except (ValueError, AssertionError):
        flash("Enter crop, market and a valid price.", "error")
    else:
        execute("INSERT INTO market_prices(crop,market,price_per_kg,price_date) VALUES(?,?,?,?)",
                (f["crop"].strip().title(), f["market"].strip(), price, f.get("price_date") or date.today().isoformat()))
        flash("Market price added.", "ok")
    return redirect(url_for("admin"))

@app.route("/admin/price/<int:pid>/delete", methods=["POST"])
@login_required("admin")
def admin_price_delete(pid):
    execute("DELETE FROM market_prices WHERE id=?", (pid,))
    flash("Price entry deleted.", "ok")
    return redirect(url_for("admin"))

@app.errorhandler(403)
@app.errorhandler(404)
def error(e):
    return render_template("error.html", e=e), e.code

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)
