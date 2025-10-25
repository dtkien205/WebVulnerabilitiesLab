DROP DATABASE IF EXISTS blindlogin;
CREATE DATABASE blindlogin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE blindlogin;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- FLAG chính là mật khẩu của admin
INSERT INTO users(username, password)
VALUES ('admin', 'FLAG{blind_boolean_login_so_easy}');