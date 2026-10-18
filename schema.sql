-- =============================================================================
-- FALCONXOFT INTERN EVALUATION — PROJECT 02: E-COMMERCE STORE
-- Database Engine: PostgreSQL 18
-- Target Database: ecommerce_db
-- Author: Talha Ahmed
-- =============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table (Customer & Admin Roles)
CREATE TABLE IF NOT EXISTS users_user (
    id BIGSERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMPTZ NULL,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL DEFAULT '',
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    role VARCHAR(20) NOT NULL DEFAULT 'customer' CHECK (role IN ('customer', 'admin')),
    phone VARCHAR(30) NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_ecom_user_role ON users_user (role);

-- 2. Product Catalog Table (With Hard Database Check Constraints)
CREATE TABLE IF NOT EXISTS products_product (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(300) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0), -- HARD NEGATIVE STOCK PREVENTION
    sku VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL DEFAULT 'electronics',
    image_url VARCHAR(200) NOT NULL DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_product_cat_active ON products_product (category, is_active);
CREATE INDEX IF NOT EXISTS idx_product_stock ON products_product (stock);
CREATE INDEX IF NOT EXISTS idx_product_sku ON products_product (sku);

-- 3. Shopping Cart & Line Items
CREATE TABLE IF NOT EXISTS cart_cart (
    id BIGSERIAL PRIMARY KEY,
    session_key VARCHAR(64) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id BIGINT UNIQUE NULL REFERENCES users_user(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS cart_cartitem (
    id BIGSERIAL PRIMARY KEY,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cart_id BIGINT NOT NULL REFERENCES cart_cart(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products_product(id) ON DELETE CASCADE,
    UNIQUE (cart_id, product_id)
);

-- 4. Payment Transactions (Audit Log with Idempotency Key)
CREATE TABLE IF NOT EXISTS payments_paymenttransaction (
    id BIGSERIAL PRIMARY KEY,
    idempotency_key VARCHAR(100) NOT NULL UNIQUE,
    amount NUMERIC(10, 2) NOT NULL,
    payment_token VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'declined', 'error')),
    gateway_message VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id BIGINT NOT NULL REFERENCES users_user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_payment_idempotency ON payments_paymenttransaction (idempotency_key);
CREATE INDEX IF NOT EXISTS idx_payment_user_status ON payments_paymenttransaction (user_id, status);

-- 5. Orders (Lifecycle & State Machine)
CREATE TABLE IF NOT EXISTS orders_order (
    id BIGSERIAL PRIMARY KEY,
    order_number VARCHAR(64) NOT NULL UNIQUE,
    total_amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled')),
    shipping_address TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    payment_transaction_id BIGINT UNIQUE NULL REFERENCES payments_paymenttransaction(id) ON DELETE SET NULL,
    user_id BIGINT NOT NULL REFERENCES users_user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_order_user_created ON orders_order (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_order_status ON orders_order (status);
CREATE INDEX IF NOT EXISTS idx_order_number ON orders_order (order_number);

-- 6. Order Line Items (Immutable Historical Price Snapshots)
CREATE TABLE IF NOT EXISTS orders_orderitem (
    id BIGSERIAL PRIMARY KEY,
    product_title VARCHAR(255) NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL, -- FROZEN PURCHASE PRICE
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    subtotal NUMERIC(10, 2) NOT NULL,
    order_id BIGINT NOT NULL REFERENCES orders_order(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products_product(id) ON DELETE PROTECT
);
