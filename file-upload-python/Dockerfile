FROM python:3.11-slim

WORKDIR /app

# Cài đặt PHP-CGI để thực thi file PHP
RUN apt-get update && \
    apt-get install -y php-cgi && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements và cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .
COPY templates/ ./templates/

# Tạo thư mục uploads
RUN mkdir -p uploads

# Tạo flag file
RUN echo "FLAG{upl0ad_php_sh3ll_and_rc3_1s_fun!}" > /app/flag.txt && \
    chmod 644 /app/flag.txt

# Tạo thêm một số file nhử
RUN echo "This is not the flag" > /etc/readme.txt && \
    echo "Keep looking..." > /var/log/hint.txt

# Chạy với user không phải root (làm cho việc tìm flag khó hơn một chút)
RUN useradd -m -u 1000 ctfuser && \
    chown -R ctfuser:ctfuser /app && \
    chmod 644 /app/flag.txt

USER ctfuser

EXPOSE 5000

CMD ["python", "app.py"]
