DROP DATABASE IF EXISTS tech_shop_db;

CREATE DATABASE tech_shop_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE tech_shop_db;

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE TABLE categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE manufacturers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model VARCHAR(150) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    warranty_months INT,
    category_id INT NOT NULL,
    manufacturer_id INT NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id)
);

CREATE TABLE suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE supplies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    supply_date DATE NOT NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

CREATE TABLE supply_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supply_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    purchase_price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (supply_id) REFERENCES supplies(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_date DATETIME NOT NULL,
    status VARCHAR(30) NOT NULL,
    delivery_address VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);


INSERT INTO roles (name) VALUES ('Admin');
INSERT INTO users (login, password, role_id) VALUES ('admin', '1234', 1);

INSERT INTO categories (name) VALUES ('Смартфоны'), ('Ноутбуки');
INSERT INTO manufacturers (name) VALUES ('Apple'), ('Samsung');

INSERT INTO products (model, price, warranty_months, category_id, manufacturer_id) VALUES 
('iPhone 15', 90000, 12, 1, 1),
('Galaxy S24', 80000, 12, 1, 2),
('MacBook Air', 120000, 24, 2, 1);