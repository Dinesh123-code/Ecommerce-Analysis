CREATE DATABASE IF NOT EXISTS ecommerce_db;
USE ecommerce_db;

CREATE TABLE IF NOT EXISTS ecommerce_sales (
    order_id VARCHAR(64) NOT NULL,
    order_date DATE NOT NULL,
    customer_id VARCHAR(64) NOT NULL,
    customer_name VARCHAR(255),
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    region VARCHAR(100) NOT NULL,
    quantity INT DEFAULT 0,
    unit_price DECIMAL(12, 2) DEFAULT 0,
    cost DECIMAL(12, 2) DEFAULT 0,
    revenue DECIMAL(12, 2) DEFAULT 0,
    profit DECIMAL(12, 2) DEFAULT 0
);
