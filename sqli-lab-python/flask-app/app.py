# flask-app/app.py
from flask import Flask, request, g, render_template, redirect, url_for, session
import pymysql
import os
import time

DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = int(os.environ.get("DB_PORT", 3306))
DB_NAME = os.environ.get("DB_NAME", "sqli_lab")
DB_USER = os.environ.get("DB_USER", "lab")
DB_PASS = os.environ.get("DB_PASS", "labpassword")
SECRET_KEY = os.environ.get("FLASK_SECRET", "devsecret")

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        # reconnect if necessary
        g._db = pymysql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
            charset='utf8mb4'
        )
        db = g._db
    return db

@app.teardown_appcontext
def close_db(e=None):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    user = session.get("username")
    return render_template("index.html", user=user)

@app.route("/login", methods=["GET","POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username","")
        password = request.form.get("password","")

        db = get_db()

        # === VULNERABLE LOGIN: string interpolation -> SQLi ===
        # Do NOT use this in production.
        query = f"SELECT id, username FROM users WHERE username = '{username}' AND password = '{password}';"
        try:
            with db.cursor() as cur:
                cur.execute(query)
                row = cur.fetchone()
        except Exception as e:
            row = None
            error = f"DB error: {e}"

        if row:
            session['user_id'] = row['id']
            session['username'] = row['username']
            return redirect(url_for('index'))
        else:
            error = error or "Invalid credentials"

    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

def require_login():
    return 'username' in session

@app.route("/product")
def product():
    if not require_login():
        return redirect(url_for("login"))

    product_id = request.args.get("product_id", "1")
    db = get_db()

    # === VULNERABLE PRODUCT QUERY: SQLi possible ===
    query = f"SELECT id, name, description, price FROM products WHERE id = {product_id};"
    try:
        with db.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
    except Exception as e:
        rows = []
        error = str(e)
    else:
        error = None

    return render_template("product.html", query=query, rows=rows, error=error)

if __name__ == "__main__":
    # optional small wait to help when MySQL startup is slow in some environments
    time.sleep(1)
    app.run(host="0.0.0.0", port=5000, debug=True)
