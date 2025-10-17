# Twig SSTI Lab (PHP + Twig)


## Giới thiệu
Lab mô phỏng lỗ hổng **SSTI (Server‑Side Template Injection)** trong **Twig**. Ứng dụng cố tình **nhúng trực tiếp** dữ liệu người dùng vào **chuỗi template** rồi render bằng `createTemplate(...)->render(...)`, khiến Twig biên dịch và thực thi biểu thức do người dùng cung cấp.

---

## Cấu trúc thư mục
```
twig-ssti-lab/
├─ composer.json
├─ Dockerfile
├─ docker-compose.yml
├─ README.md
├─ templates/
│  ├─ base.html.twig
│  └─ safe.html.twig
└─ public/
   ├─ index.php         # trang có lỗ hổng SSTI
   └─ safe.php          # trang an toàn (đã fix)
```

---


## Chạy lab
```bash
docker compose up --build
# Mở:
#   http://127.0.0.1:4001/index.php   (vulnerable)
#   http://127.0.0.1:4001/safe.php    (safe)
```

---

## Khai thác
- **Kiểm tra SSTI**: `{{ 7 * 7 }}` → `49`
- **RCE (demo)**: `{{ exec('id') }}`, `{{ exec('uname -a') }}`  
  *Cố tình đăng ký TwigFunction `exec` trỏ `shell_exec` để minh hoạ nguy cơ khi template engine có thể gọi hàm PHP*

---

## Vì sao bị SSTI? Vì sao bản safe không?
- `/index.php`: dùng `createTemplate(STRING)->render(...)` với STRING chứa **input người dùng** ⇒ Twig biên dịch biểu thức ⇒ **SSTI**.
- `/safe.php`: dùng **template cố định** + `{{ q }}` (auto-escape) ⇒ input **không** bị biên dịch ⇒ **không SSTI**.

---

