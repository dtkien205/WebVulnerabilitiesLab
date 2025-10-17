FROM python:3.12-slim

# Tạo user không phải root để chạy app cho an toàn hơn một chút (lab vẫn khai thác trong user này)
RUN useradd -ms /bin/bash appuser
WORKDIR /app

# Cài gói hệ thống tối thiểu (nếu cần) và deps Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy mã nguồn
COPY . .

# Quyền sở hữu để chạy bằng appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 4000
CMD ["python", "app.py"]
