import os
from urllib.parse import unquote
from flask import Flask, request, make_response, render_template
import mysql.connector

app = Flask(__name__)

DB_CFG = {
    'host': os.getenv('DB_HOST', '127.0.0.1'),
    'user': os.getenv('DB_USER', 'app'),
    'password': os.getenv('DB_PASS', 'app123'),
    'database': os.getenv('DB_NAME', 'sqli_lab'),
}

def get_db():
    return mysql.connector.connect(**DB_CFG)

@app.route('/')
def index():
    # Dùng cookie TrackingId 
    raw = request.cookies.get('TrackingId', 'guest')
    tracking_id = unquote(raw)

    # CỐ Ý GHÉP CHUỖI (KHÔNG DÙNG PARAMETERIZED QUERY)
    sql = (
        "SELECT username FROM users "
        f"WHERE tracking_id = '{tracking_id}'"
    )

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        cur.close(); conn.close()

        if row:
            username = row[0]
            resp = make_response(render_template('index.html', message=f"Welcome back, {username}!", last_sql=sql, error=None))
        else:
            # Không tìm thấy → hiển thị dạng khách
            resp = make_response(render_template('index.html', message="Hello, guest.", last_sql=sql, error=None))
    except mysql.connector.Error as e:
        # In RÕ thông báo lỗi và cả câu SQL → điều kiện cho error‑based SQLi
        err = f"MySQL Error {e.errno}: {e.msg}"
        resp = make_response(render_template('index.html', message="Database error!", last_sql=sql, error=err))

    # Nếu chưa có cookie, set để tiện test
    if 'TrackingId' not in request.cookies:
        resp.set_cookie('TrackingId', 'kido')  # cookie mặc định
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)