-- DSP Eco Tracker Production Database Schema

CREATE DATABASE dsp_eco_tracker;
USE dsp_eco_tracker;

-- Users table for authentication
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table (migrated from CSV)
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(500) NOT NULL,
    material VARCHAR(100),
    weight DECIMAL(10,2),
    transport VARCHAR(50),
    recyclability VARCHAR(50),
    true_eco_score VARCHAR(10),
    co2_emissions DECIMAL(10,2),
    origin VARCHAR(100),
    category VARCHAR(100),
    search_term VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_material (material),
    INDEX idx_origin (origin),
    INDEX idx_category (category)
);

-- Scraped products from user submissions
CREATE TABLE scraped_products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    amazon_url VARCHAR(1000) NOT NULL,
    asin VARCHAR(20),
    title VARCHAR(500),
    price DECIMAL(10,2),
    weight DECIMAL(10,2),
    material VARCHAR(100),
    brand VARCHAR(200),
    origin_country VARCHAR(100),
    confidence_score DECIMAL(3,2),
    scraping_status ENUM('success', 'partial', 'failed') DEFAULT 'success',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_asin (asin),
    INDEX idx_brand (brand)
);

-- Emission calculations and predictions
CREATE TABLE emission_calculations (
    id INT PRIMARY KEY AUTO_INCREMENT,
    scraped_product_id INT,
    user_postcode VARCHAR(20),
    transport_distance DECIMAL(10,2),
    transport_mode VARCHAR(50),
    ml_prediction DECIMAL(10,2),
    rule_based_prediction DECIMAL(10,2),
    final_emission DECIMAL(10,2),
    confidence_level DECIMAL(3,2),
    calculation_method VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scraped_product_id) REFERENCES scraped_products(id),
    INDEX idx_postcode (user_postcode)
);

-- Admin review queue
CREATE TABLE admin_reviews (
    id INT PRIMARY KEY AUTO_INCREMENT,
    scraped_product_id INT,
    review_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    admin_notes TEXT,
    reviewed_by INT,
    reviewed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (scraped_product_id) REFERENCES scraped_products(id),
    FOREIGN KEY (reviewed_by) REFERENCES users(id)
);