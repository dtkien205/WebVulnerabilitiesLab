import os
import ipaddress
from urllib.parse import urlparse

import requests
from flask import Flask, request, render_template, Response, abort

app = Flask(__name__)

# Chỉ tìm chuỗi trong URL, KHÔNG resolve DNS, KHÔNG chặn các biểu diễn IP khác
BAD_DENYLIST_SUBSTR = [
    'localhost', '127.0.0.1', '0.0.0.0', '::1', '169.254.169.254'
]

def naive_block(url: str) -> bool:
    url_l = url.lower()
    return any(bad in url_l for bad in BAD_DENYLIST_SUBSTR)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/fetch")
def fetch():
    url = request.args.get("url", "").strip()
    if not url:
        return Response("Thiếu tham số ?url=...", status=400)

    # Chặn theo chuỗi → dễ bị bypass
    if naive_block(url):
        return Response("Forbidden", status=400)

    try:
        # Không đặt timeout, không kiểm tra IP/host thực → SSRF
        r = requests.get(url, allow_redirects=True)
        content = r.text
        # Trả nguyên văn nội dung từ server đích
        return Response(content, status=r.status_code, headers={'Content-Type': r.headers.get('Content-Type', 'text/plain')})
    except Exception as e:
        return Response(f"Lỗi yêu cầu: {e}", status=500)

@app.route("/admin")
def admin_only():

    # Khi bị SSRF: server sẽ tự gọi chính nó → remote_addr là 127.0.0.1
    remote = request.remote_addr or ''
    try:
        ip = ipaddress.ip_address(remote)
        if not ip.is_loopback:
            abort(403)
    except ValueError:
        abort(403)

    flag = os.getenv("FLAG", "flag{default}")
    return render_template("admin.html", flag=flag)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
