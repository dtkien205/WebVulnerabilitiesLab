# XSS Lab (Reflected • Stored • DOM)

## Chạy bằng Python thuần
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py

Mở: `http://localhost:5001`

## Chạy bằng Docker
docker compose up --build -d

Mở: `http://localhost:5001`

---

## 1) Reflected XSS
URL mẫu:
- `http://localhost:5001/?q=<script>alert(1)</script>`
- `http://localhost:5001/?q=<img src=x onerror=alert(1)>`

Nguyên nhân: biến q được render với `|safe` → phản chiếu trực tiếp.

## 2) Stored XSS
- Vào `http://localhost:5001/comments`
- Gửi bình luận: `<script>alert('Stored XSS')</script>`
- Reload lại trang → script chạy từ DB.

Nguyên nhân: nội dung bình luận render với `|safe`.

## 3) DOM-based XSS
URL mẫu:
- `http://localhost:5001/dom?msg=<svg/onload=alert(1)>`
- `http://localhost:5001/dom#<svg/onload=alert(1)>`

Nguyên nhân: JS lấy `?msg` hoặc `#hash` rồi `innerHTML` trực tiếp.
