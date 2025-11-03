import os
import re
from flask import Flask, request, render_template, render_template_string

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"
app.config["DEMO_NOTE"] = "SSTI demo"

# Tạo flag
FLAG_PATH = os.path.join(os.path.dirname(__file__), "flag.txt")
if not os.path.exists(FLAG_PATH):
    with open(FLAG_PATH, "w", encoding="utf-8") as f:
        f.write("FLAG{this_is_demo_flag_for_SSTI_lab_only}\n")

# ===== WAF =====
BLACKLIST_PATTERNS = [
    (re.compile(r"\.", re.IGNORECASE), "'.'"),
    (re.compile(r"_", re.IGNORECASE), "'_'"),
    (re.compile(r"\|\s*join", re.IGNORECASE), "'|join'"),
    (re.compile(r"\[", re.IGNORECASE), "'['"),
    (re.compile(r"\]", re.IGNORECASE), "']'"),
    (re.compile(r"\bmro\b", re.IGNORECASE), "'mro'"),
    (re.compile(r"\bbase\b", re.IGNORECASE), "'base'"),
]

def get_block_reason(s: str):
    """Trả về label token đầu tiên khiến bị chặn, hoặc None nếu pass."""
    for rx, label in BLACKLIST_PATTERNS:
        if rx.search(s):
            return label
    return None

# chặn xss cơ bản
def escape_angle(s: str) -> str:
    return s.replace("<", "&lt;").replace(">", "&gt;")


@app.route("/", methods=["GET", "POST"])
def index():
    default_msg = ""
    q = request.values.get("q", default_msg)

    # Kiểm tra WAF
    reason = get_block_reason(q)
    blocked_banner = ""
    if reason:
        blocked_banner = f"""
        <div class="card" style="border-color:#ef4444">
          <strong>Forbidden token: <code>{reason}</code></strong>
        </div>
        """

    # Template khung 
    vulnerable_template = """
    {% extends "base.html" %}
    {% block content %}
      <h2>Nhập username </h2>
      <form method="post" action="/">
        <input type="text" name="q" style="width: 100%%" value="{{ q|e }}">
        <button type="submit">Gửi</button>
      </form>

      %BLOCKED_BANNER%

      <div class="card">
        <strong>Xin chào: %PAYLOAD%</strong>
      </div>

    {% endblock %}
    """

    if reason:
        vulnerable_template = vulnerable_template.replace("%PAYLOAD%", "{{ q|e }}")
    else:
        safe_input = escape_angle(q)
        vulnerable_template = vulnerable_template.replace("%PAYLOAD%", safe_input)

    vulnerable_template = vulnerable_template.replace("%BLOCKED_BANNER%", blocked_banner)

    # Render bằng Jinja2 (giữ nguyên bản chất SSTI khi không bị chặn)
    html = render_template_string(vulnerable_template, q=q)
    return html


@app.route("/safe-preview")
def safe_preview():
    q = request.args.get("q", "")
    return render_template("index.html", q=q)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)
