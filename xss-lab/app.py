import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
DB_PATH = os.path.join(os.path.dirname(__file__), 'xsslab.sqlite3')

def init_db():
    """Tạo bảng nếu chưa có và seed dữ liệu mẫu cho items."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Bảng comments (demo Stored XSS)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            content TEXT NOT NULL
        )
    """)

    # Bảng items (truy vấn theo id trên trang reflected)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL DEFAULT 0.0,
            description TEXT DEFAULT ''
        )
    """)

    # Seed dữ liệu items nếu trống
    cur.execute("SELECT COUNT(*) FROM items")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO items(name, price, description) VALUES (?, ?, ?)",
            [
                ("Blue Widget", 9.99, "A small blue widget."),
                ("Red Gadget", 19.50, "Red gadget with multiple uses."),
                ("Pro Hammer", 49.90, "Professional grade hammer."),
                ("Deluxe Chair", 129.99, "Comfortable deluxe chair."),
            ]
        )

    conn.commit()
    conn.close()

# GỌI TRỰC TIẾP KHI APP KHỞI ĐỘNG
init_db()

# 1) REFLECTED XSS
@app.route('/')
def index_reflected():
    # q dùng để demo JS-context XSS trong template
    q = request.args.get('q', '')

    # Nếu q là số -> truy vấn items theo id
    item = None
    try:
        q_int = int(q)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT id, name, price, description FROM items WHERE id = ?", (q_int,))
        item = cur.fetchone()
        conn.close()
    except Exception:
        # q không phải số (hoặc lỗi) -> không truy vấn
        pass

    return render_template('index_reflected.html', q=q, item=item)

# 2) STORED XSS
@app.route('/comments', methods=['GET', 'POST'])
def comments_stored():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if request.method == 'POST':
        author = request.form.get('author', 'anonymous')
        content = request.form.get('content', '')
        # LỖ HỔNG: lưu raw content, render lại với |safe => Stored XSS
        cur.execute("INSERT INTO comments(author, content) VALUES (?, ?)", (author, content))
        conn.commit()
        conn.close()
        return redirect(url_for('comments_stored'))

    cur.execute("SELECT id, author, content FROM comments ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return render_template('comments_stored.html', rows=rows)

# 3) DOM-BASED XSS
@app.route('/dom')
def dom_based():
    # LỖ HỔNG ở JS: lấy query/hash và innerHTML thẳng vào DOM (trong template)
    return render_template('dom_based.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
