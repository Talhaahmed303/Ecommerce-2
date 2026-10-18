-- =============================================================================
-- FALCONXOFT INTERN EVALUATION — PROJECT 02: HIGH-INTEGRITY E-COMMERCE STORE
-- Database DDL for Lucidchart ERD Import (File -> Import Data -> ERD -> PostgreSQL)
-- Candidate: Talha Ahmed | Date: October 2026
-- =============================================================================

CREATE TABLE users_user (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'customer' CHECK (role IN ('customer', 'admin')),
    phone VARCHAR(30) NOT NULL DEFAULT '',
    address TEXT NOT NULL DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    date_joined TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products_product (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(300) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    sku VARCHAR(50) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL DEFAULT 'electronics',
    image_url VARCHAR(200) NOT NULL DEFAULT '',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cart_cart (
    id BIGSERIAL PRIMARY KEY,
    session_key VARCHAR(64) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id BIGINT UNIQUE NULL REFERENCES users_user(id) ON DELETE CASCADE
);

CREATE TABLE cart_cartitem (
    id BIGSERIAL PRIMARY KEY,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    cart_id BIGINT NOT NULL REFERENCES cart_cart(id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES products_product(id) ON DELETE CASCADE,
    CONSTRAINT uq_cart_product UNIQUE (cart_id, product_id)
);

CREATE TABLE payments_paymenttransaction (
    id BIGSERIAL PRIMARY KEY,
    idempotency_key VARCHAR(100) NOT NULL UNIQUE,
    amount NUMERIC(10, 2) NOT NULL,
    payment_token VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('success', 'declined', 'error')),
    gateway_message VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id BIGINT NOT NULL REFERENCES users_user(id) ON DELETE CASCADE
);

CREATE TABLE orders_order (
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

CREATE TABLE orders_orderitem (
    id BIGSERIAL PRIMARY KEY,
    product_title VARCHAR(255) NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    subtotal NUMERIC(10, 2) NOT NULL,
    order_id BIGINT NOT NULL REFERENCES orders_order(id) ON DELETE CASCADE,
    product_id BIGINT NULL REFERENCES products_product(id) ON DELETE SET NULL
);

-- Strategic Query & Concurrency Indexes
CREATE INDEX idx_product_stock ON products_product (stock);
CREATE INDEX idx_payment_idempotency ON payments_paymenttransaction (idempotency_key);
CREATE INDEX idx_order_user_created ON orders_order (user_id, created_at DESC);
CREATE INDEX idx_order_status ON orders_order (status);
