DROP DATABASE IF EXISTS sqli_lab;
CREATE DATABASE sqli_lab CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE sqli_lab;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    tracking_id VARCHAR(255) NOT NULL
);
CREATE TABLE flags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    flag TEXT NOT NULL
);
INSERT INTO users (username, password, tracking_id)
VALUES ('admin', 'admin123', 'kido'),
    ('alice', 'alicepass', 't001'),
    ('bob', 'bobpass', 't002'),
    ('charlie', 'charliepass', 't003'),
    ('david', 'davidpass', 't004'),
    ('eva', 'evapass', 't005'),
    ('frank', 'frankpass', 't006'),
    ('grace', 'gracepass', 't007'),
    ('heidi', 'heidipass', 't008'),
    ('ivan', 'ivanpass', 't009'),
    ('judy', 'judypass', 't010');
-- Flag mẫu
INSERT INTO flags(flag)
VALUES('FLAG{demo_error_based_sqli_lab}');