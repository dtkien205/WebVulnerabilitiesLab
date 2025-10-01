-- db/mysql-init.sql
CREATE DATABASE IF NOT EXISTS sqli_lab CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE sqli_lab;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(100) NOT NULL
);

DROP TABLE IF EXISTS products;
CREATE TABLE products (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(255),
  description TEXT,
  price DECIMAL(10,2)
);

DROP TABLE IF EXISTS flag;
CREATE TABLE flag (
  id INT AUTO_INCREMENT PRIMARY KEY,
  flag VARCHAR(100) NOT NULL
);

INSERT INTO users (username, password) VALUES
('admin','adminpass'),
('alice','alicepass');

INSERT INTO products (name,description,price) VALUES
('Blue Widget','A small blue widget.',9.99),
('Red Gadget','Handy red gadget.',19.50),
('Deluxe Chair','Comfortable deluxe chair.',129.99);

INSERT INTO flag (flag) VALUES
('FLAG{sql_injection_success}');
