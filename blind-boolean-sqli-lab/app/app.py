import os
from flask import Flask, request, render_template, redirect, url_for

import mysql.connector

app = Flask(__name__)

DB_CFG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "appuser"),
    "password": os.getenv("DB_PASS", "apppass"),
    "database": os.getenv("DB_NAME", "blindlogin"),
}

def get_db():
    return mysql.connector.connect(**DB_CFG)

@app.route("/", methods=["GET"])
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    msg = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # LỖ HỔNG: nối chuỗi trực tiếp vào SQL -> Blind Boolean-based SQLi
        query = (
            "SELECT id FROM users "
            f"WHERE username = '{username}' AND password = '{password}' LIMIT 1"
        )

        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute(query)
            row = cur.fetchone()
            if row:
                msg = ("success", f"Đăng nhập thành công! Xin chào {username}.")
            else:
                msg = ("fail", "Đăng nhập thất bại.")
        except Exception:
            # Không lộ lỗi để giữ dạng 'blind'
            msg = ("fail", "Đăng nhập thất bại.")
        finally:
            try:
                cur.close()
                conn.close()
            except Exception:
                pass

    return render_template("login.html", msg=msg)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
