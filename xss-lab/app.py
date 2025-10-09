import os
import sqlite3
from flask import Flask, request, render_template, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
DB_PATH = os.path.join(os.path.dirname(__file__), 'xsslab.sqlite3')

def init_db():
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE comments(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

# GỌI TRỰC TIẾP KHI APP KHỞI ĐỘNG
init_db()

# 1) REFLECTED XSS
@app.route('/')
def index_reflected():
    # LỖ HỔNG: trả lại trực tiếp chuỗi 'q' theo kiểu unsafe trong template (|safe)
    q = request.args.get('q', '')
    return render_template('index_reflected.html', q=q)

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
    # Trang này không render gì nguy hiểm từ server.
    # LỖ HỔNG ở JS: lấy query/hash và .innerHTML thẳng vào DOM.
    return render_template('dom_based.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
