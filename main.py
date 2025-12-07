from flask import Flask, render_template, request, redirect, url_for
from database import get_db_connection

app = Flask(__name__, static_url_path="/static", static_folder="static")

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")


@app.route("/catalog", methods=["GET"])
def catalog():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    data = [dict(r) for r in rows]
    conn.close()
    return render_template("catalog.html", catalog=data)


@app.route("/add_item", methods=["POST"])
def add_item():
    title = request.form["title"]
    description = request.form["description"]
    try:
        price = float(request.form["price"])
    except ValueError:
        return "Введено неправильний формат ціни", 400

    image_url = request.form["image_url"]
    category = request.form["category"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(products);")
    cols = [row['name'] for row in cursor.fetchall()]
    if 'category' not in cols:
        cursor.execute("ALTER TABLE products ADD COLUMN category TEXT;")
    cursor.execute(
        "INSERT INTO products (title, description, price, image_url, category) VALUES (?, ?, ?, ?, ?)",
        (title, description, price, image_url, category),
    )
    conn.commit()
    conn.close()
    
    return redirect(url_for('catalog'))

@app.route("/remove_item", methods=["POST"])
def remove_item():
    item_id = request.form["id"]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('catalog'))

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html"), 404

@app.route("/filter_catalog", methods=["GET"])
def filter_catalog():
    category = request.args.get("category", "")
    min_price_str = request.args.get("min_price")
    max_price_str = request.args.get("max_price")

    conn = get_db_connection()
    cursor = conn.cursor()

    base_query = "SELECT * FROM products"
    conditions = []
    params = []

    if category:
        conditions.append("category = ?")
        params.append(category)

    try:
        min_price = float(min_price_str)
        if min_price > 0:
            conditions.append("price >= ?")
            params.append(min_price)
    except (ValueError, TypeError):
        pass 

    try:
        max_price = float(max_price_str)
        if max_price > 0:
            conditions.append("price <= ?")
            params.append(max_price)
    except (ValueError, TypeError):
        pass
    
    if conditions:
        query = base_query + " WHERE " + " AND ".join(conditions)
    else:
        query = base_query
    
    cursor.execute(query, tuple(params))
        
    data = cursor.fetchall()
    conn.close()
    
    return render_template(
        "catalog.html", catalog=data
    )