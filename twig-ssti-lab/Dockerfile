FROM php:8.2-apache

# Tiện ích + curl để cài Composer
RUN apt-get update && apt-get install -y --no-install-recommends git unzip curl \
    && rm -rf /var/lib/apt/lists/*

# Bật mod_rewrite (không bắt buộc)
RUN a2enmod rewrite

# Cài Composer trực tiếp
RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" \
    && php composer-setup.php --install-dir=/usr/bin --filename=composer \
    && rm composer-setup.php

# Đặt DocumentRoot về /public (để mount public/ mà không đè vendor/)
RUN sed -i 's|DocumentRoot /var/www/html|DocumentRoot /var/www/html/public|' /etc/apache2/sites-available/000-default.conf

WORKDIR /var/www/html

# Cài vendor trước (tối ưu cache)
COPY composer.json ./
ENV COMPOSER_ALLOW_SUPERUSER=1
RUN composer install --no-interaction --no-dev --prefer-dist --no-progress

# Copy mã nguồn (để image tự chạy nếu không mount)
COPY templates/ /var/www/html/templates/
COPY public/ /var/www/html/public/

# Quyền
RUN chown -R www-data:www-data /var/www/html

EXPOSE 80
