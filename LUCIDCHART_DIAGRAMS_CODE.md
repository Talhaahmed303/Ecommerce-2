# FALCONXOFT WEEKEND 1 — PROJECT 02 (E-COMMERCE) LUCIDCHART DIAGRAM CODES

**Author:** Talha Ahmed  
**Live Editable Architecture:** [Open Architecture in Lucidchart](https://lucid.app/lucidchart/6ef90429-d6a5-4585-8b7f-2caaf728b0fc/edit?viewport_loc=-5287%2C321%2C16525%2C6279%2C0_0&invitationId=inv_9b2b97cf-501b-429e-993d-a24c927fa54c)  
**Live Editable Database ERD:** [Open Database ERD in Lucidchart](https://lucid.app/lucidchart/fc2bb308-385a-44aa-8eec-6b89b42e11a7/edit?viewport_loc=-1034%2C-301%2C5760%2C2794%2C0_0&invitationId=inv_617b723e-1db7-444f-9378-4db505be3b4b)

This document contains the exact, up-to-date Mermaid and SQL definitions for all 3 required diagrams in Project 02. You can directly copy these codes and import them into Lucidchart via **File ➔ Import Data ➔ Mermaid** or paste them into any Markdown viewer.

---

## 1. System Architecture Diagram (`02 - architecture.pdf`)

```mermaid
%% =============================================================================
%% FALCONXOFT INTERN EVALUATION — PROJECT 02: HIGH-INTEGRITY E-COMMERCE STORE
%% System Architecture Diagram (Lucidchart / Mermaid Compatible)
%% Candidate: Talha Ahmed | Date: October 2026
%% =============================================================================

flowchart TD
    subgraph CLIENT_TIER ["1. Presentation Layer (Storefront Browser)"]
        Browser["🌐 Web Browser (Customer / Admin / Guest)"]
        NextApp["⚡ Next.js 14 (React 18 + TypeScript + Tailwind CSS)<br/><b>Port 3002</b>"]
        Browser -->|"HTTP / UI Interaction"| NextApp
        
        subgraph CLIENT_COMPONENTS ["Storefront Modules & Interactive UIs"]
            CatalogView["🛍️ Store Catalog & 280ms Debounced Search<br/>(Live Category Filter & Stock Status Badges)"]
            ProductDetailModal["👁️ Product Detail / Quick View Modal<br/>(High-Res Image, Specs, Qty Stepper, Buy Now)"]
            CartDrawer["🛒 Sliding Cart Drawer<br/>(Guest LocalStorage & Authenticated Sync)"]
            CheckoutModal["💳 Atomic Checkout Modal<br/>(tok_success vs tok_decline Card Simulation)"]
            OrderHistory["📦 Orders & Price-Frozen Receipts<br/>(Strict Cross-Customer Privacy Isolation)"]
            AdminFulfill["👑 Admin Fulfillment & Live Stock Replenishment<br/>(FSM Terminal State: DELIVERED Lock)"]
            DemoSwitcher["👥 Fast Demo User Persona Switcher<br/>(Talha Ahmed / Alice Buyer / Sara / Admin / Guest)"]
        end
        NextApp --- CLIENT_COMPONENTS
        CatalogView -->|"Click Card / Details Button"| ProductDetailModal
        ProductDetailModal -->|"Add Qty / Buy Now"| CartDrawer
        CartDrawer -->|"Proceed to Checkout"| CheckoutModal
        TokenStore[("🔑 LocalStorage<br/>JWT Access/Refresh & Guest Cart")]
        NextApp -.->|"Token & Session Persistence"| TokenStore
    end

    subgraph NETWORK_BOUNDARY ["Communication Protocols & Security Boundary"]
        RestCall["HTTPS / REST API Requests<br/><code>Authorization: Bearer &lt;JWT&gt;</code><br/>Content-Type: application/json"]
        CorsGuard["🛡️ CORS Middleware<br/>Allowed Origins: http://localhost:3002"]
    end

    NextApp ==>|"REST API Calls"| RestCall
    RestCall ==>|"CORS Inspected"| CorsGuard

    subgraph API_TIER ["2. Application & API Layer (Host Bare-Metal)"]
        CorsGuard ==>|"Dispatched to DRF"| DRF["🚀 Django 5.2 + Django REST Framework<br/><b>Port 8002</b>"]
        
        subgraph SECURITY_GUARD ["Security & Permission Guards"]
            JWTAuth["🔐 SimpleJWT Authentication<br/>(HMAC-SHA256 Token Verification)"]
            RBAC["🛡️ Role-Based Access Control<br/>(Customer vs Admin Permissions)"]
        end
        DRF --> SECURITY_GUARD

        subgraph CONTROLLERS ["Domain ViewSets & Core Services"]
            ProdAPI["📦 ProductViewSet<br/><code>/api/products/, /update_stock/</code><br/><i>Catalog, Search, & Admin Stock Adjust</i>"]
            CartAPI["🛒 CartViewSet<br/><code>/api/cart/, /add/, /update_quantity/</code><br/><i>Multi-Quantity Validation & Auto Subtotal</i>"]
            CheckoutSvc["⚡ Concurrency-Safe Checkout Service<br/><code>transaction.atomic()</code><br/><b>select_for_update() in Ascending ID Order</b>"]
            OrderAPI["📑 OrderViewSet<br/><code>/api/orders/, /update_status/</code><br/><i>FSM: pending->paid->shipped->delivered (Terminal)</i>"]
            PaymentMock["💳 MockPaymentGateway<br/><i>Deterministic Tokens & Idempotency</i>"]
        end
        SECURITY_GUARD --> CONTROLLERS
        CartAPI --> CheckoutSvc
        CheckoutSvc --> PaymentMock
        CheckoutSvc --> OrderAPI
    end

    subgraph DATABASE_TIER ["3. Persistent Data Layer (PostgreSQL 18)"]
        DBEngine[("🐘 PostgreSQL 18 Engine<br/><b>Port 5432 | Database: ecommerce_db</b>")]
        
        subgraph RELATIONAL_TABLES ["Relational Schema (3NF)"]
            T_User["users_customuser<br/>PK: id | role: customer, admin"]
            T_Prod["products_product<br/>PK: id | UQ: sku<br/><b>CHECK (stock >= 0)</b>"]
            T_Cart["cart_cart & cart_cartitem<br/>PK: id | FK: user_id, product_id"]
            T_Tx["payments_paymenttransaction<br/>PK: id | <b>UQ: idempotency_key</b>"]
            T_Order["orders_order<br/>PK: id | UQ: order_number<br/>status: pending, paid, shipped, delivered..."]
            T_Item["orders_orderitem<br/>PK: id | FK: order_id, product_id<br/><b>Frozen unit_price Snapshot</b>"]
        end
        DBEngine --- RELATIONAL_TABLES

        subgraph DB_INDEXES ["Performance & Integrity Indexes"]
            Idx1["idx_product_stock (stock)"]
            Idx2["idx_order_user_created (user_id, created_at DESC)"]
            Idx3["idx_payment_idempotency (idempotency_key UNIQUE)"]
            Idx4["idx_cart_user (user_id UNIQUE)"]
        end
        RELATIONAL_TABLES --- DB_INDEXES
    end

    CONTROLLERS ==>|"psycopg2-binary / Row Locks (SELECT FOR UPDATE)"| DBEngine
    DBEngine ==>|"ACID Committed Transactions"| CONTROLLERS
    DRF ==>|"JSON Response (HTTP 200, 201, 400, 403, 404)"| NextApp

    classDef client fill:#E0F2FE,stroke:#0284C7,stroke-width:2px,color:#0369A1;
    classDef api fill:#EEF2FF,stroke:#4F46E5,stroke-width:2px,color:#3730A3;
    classDef db fill:#F0FDF4,stroke:#16A34A,stroke-width:2px,color:#15803D;
    classDef security fill:#FEF3C7,stroke:#D97706,stroke-width:1.5px,color:#92400E;
```

---

## 2. Database ERD Diagram (`03 - database-design.pdf`)

```mermaid
%% =============================================================================
%% FALCONXOFT INTERN EVALUATION — PROJECT 02: HIGH-INTEGRITY E-COMMERCE STORE
%% Entity Relationship Diagram (ERD) (Lucidchart / Mermaid Compatible)
%% Candidate: Talha Ahmed | Date: October 2026
%% =============================================================================

erDiagram
    USERS_CUSTOMUSER {
        bigserial id PK "Primary Key"
        varchar username UK "Unique Username (150)"
        varchar email UK "Email Address (254)"
        varchar role "Role: 'customer' or 'admin'"
        varchar phone "Phone Number"
        text address "Shipping Address"
        boolean is_active "Active Status"
        timestamptz date_joined "Registration Date"
    }

    PRODUCTS_PRODUCT {
        bigserial id PK "Primary Key"
        varchar title "Product Name (255)"
        varchar slug UK "URL Slug (300)"
        numeric price "Unit Price (price >= 0)"
        int stock "Available Inventory (CHECK stock >= 0)"
        varchar sku UK "Stock Keeping Unit"
        varchar category "Category Classification"
        text description "Full Product Specifications"
        varchar image_url "Product Image URL"
        boolean is_active "Active Status"
        timestamptz created_at "Created Date"
    }

    CART_CART {
        bigserial id PK "Primary Key"
        bigint user_id FK "References USERS_CUSTOMUSER.id (UNIQUE)"
        varchar session_key "Guest Session Identifier"
        timestamptz created_at "Created Timestamp"
        timestamptz updated_at "Last Modified"
    }

    CART_CARTITEM {
        bigserial id PK "Primary Key"
        bigint cart_id FK "References CART_CART.id (CASCADE)"
        bigint product_id FK "References PRODUCTS_PRODUCT.id (CASCADE)"
        int quantity "Line Item Quantity (> 0)"
        timestamptz added_at "Timestamp"
    }

    PAYMENTS_PAYMENTTRANSACTION {
        bigserial id PK "Primary Key"
        varchar idempotency_key UK "Unique Idempotency Key"
        bigint user_id FK "References USERS_CUSTOMUSER.id"
        numeric amount "Transaction Amount"
        varchar payment_token "Token (tok_success/tok_decline)"
        varchar status "Status (success/declined/error)"
        varchar gateway_message "Gateway Response Message"
        timestamptz created_at "Timestamp"
    }

    ORDERS_ORDER {
        bigserial id PK "Primary Key"
        varchar order_number UK "Unique Order Number (ORD-...)"
        bigint user_id FK "References USERS_CUSTOMUSER.id (CASCADE)"
        numeric total_amount "Total Billed Amount"
        varchar status "pending|paid|processing|shipped|delivered|cancelled"
        text shipping_address "Shipping Address Destination"
        bigint payment_transaction_id FK "References PAYMENTTRANSACTION.id"
        timestamptz created_at "Order Timestamp"
        timestamptz updated_at "Last Status Update"
    }

    ORDERS_ORDERITEM {
        bigserial id PK "Primary Key"
        bigint order_id FK "References ORDERS_ORDER.id (CASCADE)"
        bigint product_id FK "References PRODUCTS_PRODUCT.id (SET NULL)"
        varchar product_title "Historical Product Title"
        numeric unit_price "Frozen Price Snapshot"
        int quantity "Billed Quantity"
        numeric subtotal "Line Total"
    }

    %% Relationships & Cardinalities
    USERS_CUSTOMUSER ||--o| CART_CART : "owns (1:1)"
    CART_CART ||--o{ CART_CARTITEM : "contains (1:N)"
    PRODUCTS_PRODUCT ||--o{ CART_CARTITEM : "referenced_in (1:N)"
    USERS_CUSTOMUSER ||--o{ ORDERS_ORDER : "places (1:N)"
    ORDERS_ORDER ||--o{ ORDERS_ORDERITEM : "itemized_in (1:N)"
    PRODUCTS_PRODUCT ||--o{ ORDERS_ORDERITEM : "historical_reference (1:N)"
    PAYMENTS_PAYMENTTRANSACTION ||--o| ORDERS_ORDER : "settles (1:1)"
    USERS_CUSTOMUSER ||--o{ PAYMENTS_PAYMENTTRANSACTION : "executes (1:N)"
```

---

## 3. API Sequence Workflows (`04 - api-workflows.pdf`)

```mermaid
%% =============================================================================
%% FALCONXOFT INTERN EVALUATION — PROJECT 02: HIGH-INTEGRITY E-COMMERCE STORE
%% API Sequence Workflows (Lucidchart / Mermaid Compatible)
%% Atomic Concurrency-Safe Checkout, Race Condition Defense, Payment Declines, & FSM
%% Candidate: Talha Ahmed | Date: October 2026
%% =============================================================================

sequenceDiagram
    autonumber
    actor Customer as 🛒 Customer (Next.js 14)
    actor Admin as 👑 Admin Fulfillment
    participant API as 🚀 DRF API (Port 8002)
    participant DB as 🐘 PostgreSQL 18 (ecommerce_db)
    participant Gateway as 💳 MockPaymentGateway

    %% -------------------------------------------------------------------------
    %% PART 1: COMPLETE SUCCESS PATH (Atomic Concurrency-Safe Checkout)
    %% -------------------------------------------------------------------------
    rect rgb(240, 253, 244)
        Note over Customer, Gateway: PART 1: COMPLETE SUCCESS PATH (Atomic Concurrency-Safe Checkout)

        Customer->>+API: POST /api/cart/add/ {product_id: 1, quantity: 2}
        API->>+DB: SELECT * FROM products_product WHERE id=1
        DB-->>-API: Product(stock=5)
        API->>+DB: INSERT/UPDATE cart_cartitem (qty=2)
        DB-->>-API: Item Saved
        API-->>-Customer: HTTP 200 OK (Cart Total Updated)

        Customer->>+API: POST /api/cart/checkout/ [Bearer JWT]<br/>{payment_token: "tok_success", idempotency_key: "IDEM-ABC123XYZ", address: "123 Main St"}
        
        Note over API, DB: BEGIN transaction.atomic()
        API->>+DB: SELECT * FROM cart_cartitem WHERE cart_user_id = user.id
        DB-->>-API: [Item(product_id=1, qty=2)]
        
        Note over API, DB: Step 2: Pessimistic Row Lock in Ascending Product ID Order
        API->>+DB: SELECT * FROM products_product WHERE id IN (1) ORDER BY id ASC FOR UPDATE
        DB-->>-API: Locked Product Record (stock = 5)
        
        Note over API: Step 3: Validate Stock (5 >= 2 passed) & Calc Total ($1,998.00)
        API->>+Gateway: process_payment(amount=1998.00, token="tok_success", key="IDEM-ABC123XYZ")
        Gateway-->>-API: PaymentTransaction(status="success", id=88)
        
        Note over API, DB: Step 4: Decrement Stock Safely
        API->>+DB: UPDATE products_product SET stock = stock - 2 WHERE id = 1 (Stock becomes 3)
        DB-->>-API: Row Updated
        
        Note over API, DB: Step 5: Create Order & Freeze Line Item Prices
        API->>+DB: INSERT INTO orders_order (order_number="ORD-TALHA-001", total=1998.00, status='paid', payment_id=88)
        DB-->>-API: Order Created (id=101)
        API->>+DB: INSERT INTO orders_orderitem (order_id=101, unit_price=999.00, qty=2, subtotal=1998.00)
        DB-->>-API: OrderItem Persisted (Price Snapshot Frozen)
        
        API->>+DB: DELETE FROM cart_cartitem WHERE cart_id = ...
        DB-->>-API: Cart Cleared
        Note over API, DB: COMMIT transaction.atomic()
        
        API-->>-Customer: HTTP 201 Created {order_number: "ORD-TALHA-001", status: "paid"}
    end

    %% -------------------------------------------------------------------------
    %% PART 2: CONCURRENCY RACE CONDITION DEFENSE (Simultaneous Checkouts for Last Unit)
    %% -------------------------------------------------------------------------
    rect rgb(254, 242, 242)
        Note over Customer, Gateway: PART 2: CONCURRENCY RACE CONDITION DEFENSE (Last 1 Unit in Stock)

        Note over Customer, DB: Thread A (Talha) and Thread B (Alice) hit /checkout at exact same millisecond
        API->>+DB: Thread A: SELECT * FROM products_product WHERE id=5 FOR UPDATE
        DB-->>-API: Thread A acquires Row Lock (stock=1)
        Note over DB: Thread B waits for Thread A lock to release
        
        API->>+DB: Thread A: UPDATE products_product SET stock = 0 WHERE id = 5
        DB-->>-API: Thread A commits & releases Row Lock
        
        Note over DB: Thread B lock acquired; inspects stock
        API->>+DB: Thread B: SELECT * FROM products_product WHERE id=5
        DB-->>-API: Locked Product Record (stock = 0)
        Note over API: Validation: product.stock (0) < requested (1)!
        API-->>-Customer: HTTP 409 Conflict {"success": false, "message": "Insufficient stock for 'Cyberpunk Keycap Set'"}
        Note over DB: Database CHECK (stock >= 0) constraint guarantees ZERO negative inventory!
    end

    %% -------------------------------------------------------------------------
    %% PART 3: PAYMENT DECLINED & SAFE ROLLBACK (tok_decline)
    %% -------------------------------------------------------------------------
    rect rgb(255, 251, 235)
        Note over Customer, Gateway: PART 3: PAYMENT DECLINE WORKFLOW (tok_decline)

        Customer->>+API: POST /api/cart/checkout/ {payment_token: "tok_decline"}
        API->>+Gateway: process_payment(token="tok_decline")
        Gateway-->>-API: PaymentTransaction(status="declined", message="Card Declined")
        Note over API, DB: ROLLBACK transaction.atomic()
        Note over API: Zero stock deducted! Cart items preserved!
        API-->>-Customer: HTTP 400 Bad Request {"success": false, "message": "Payment declined by issuing bank (tok_decline simulated failure). Stock and cart remain intact."}
    end

    %% -------------------------------------------------------------------------
    %% PART 4: ORDER FSM LIFECYCLE & IMMUTABLE TERMINAL STATES
    %% -------------------------------------------------------------------------
    rect rgb(238, 242, 255)
        Note over Admin, DB: PART 4: ORDER FSM LIFECYCLE & TERMINAL STATES
        
        Admin->>+API: PATCH /api/orders/101/update_status/ {status: "processing"}
        API->>+DB: UPDATE orders_order SET status='processing' WHERE id=101
        DB-->>-API: Status Updated
        API-->>Admin: HTTP 200 OK ("Order transitioned to PROCESSING")
        
        Admin->>+API: PATCH /api/orders/101/update_status/ {status: "shipped"}
        API->>+DB: UPDATE orders_order SET status='shipped' WHERE id=101
        DB-->>-API: Status Updated
        API-->>Admin: HTTP 200 OK ("Order transitioned to SHIPPED")
        
        Admin->>+API: PATCH /api/orders/101/update_status/ {status: "delivered"}
        API->>+DB: UPDATE orders_order SET status='delivered' WHERE id=101
        DB-->>-API: Status Updated (Terminal State Lock Engaged)
        API-->>Admin: HTTP 200 OK ("Order transitioned to DELIVERED")

        Note over Admin, API: Attempting illegal transition from Terminal State:
        Admin->>+API: PATCH /api/orders/101/update_status/ {status: "processing"}
        Note over API: FSM Validation: 'delivered' is a terminal state!
        API-->>-Admin: HTTP 400 Bad Request {"message": "Invalid status transition from 'delivered' to 'processing'. Delivered orders are immutable."}
    end
```
