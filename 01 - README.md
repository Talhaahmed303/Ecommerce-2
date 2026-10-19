# FALCONXOFT WEEKEND 1 EVALUATION — PROJECT 02: HIGH-INTEGRITY E-COMMERCE STORE

**Author:** Talha Ahmed  
**Evaluation Role:** Full-Stack Intern Performance Evaluation (Weekend 1)  
**Deliverable Number:** 01 of 10  
**Specification Reference:** Weekend Assignment.pdf §2.2 & §3  
**Implementation Status:** 100% Implemented, Seeded, Tested, and Verified  
**Active Backend Port:** `http://127.0.0.1:8002`  
**Active Frontend Port:** `http://127.0.0.1:3002`  
**GitHub Repository:** [https://github.com/Talhaahmed303/Ecommerce-2](https://github.com/Talhaahmed303/Ecommerce-2)  
**3–5 Minute Demo Video:** [Watch E-Commerce Store Demo Walkthrough](https://drive.google.com/file/d/188jZ0az2y0jtlESSNeMaqs3rUR2J5Tqg/view?usp=sharing)  
**Live Editable Architecture:** [Open Architecture in Lucidchart](https://lucid.app/lucidchart/6ef90429-d6a5-4585-8b7f-2caaf728b0fc/edit?viewport_loc=-5287%2C321%2C16525%2C6279%2C0_0&invitationId=inv_9b2b97cf-501b-429e-993d-a24c927fa54c)  
**Live Editable Database ERD:** [Open Database ERD in Lucidchart](https://lucid.app/lucidchart/fc2bb308-385a-44aa-8eec-6b89b42e11a7/edit?viewport_loc=-1034%2C-301%2C5760%2C2794%2C0_0&invitationId=inv_617b723e-1db7-444f-9378-4db505be3b4b)  
**Live Editable API Workflows Sequence:** [Open API Workflows in Lucidchart](https://lucid.app/lucidchart/1b0fe96e-3252-44ce-9d28-8ed2cf93e7d8/edit?view_items=vrvEd8gjuvU3&page=0_0&invitationId=inv_0f45dbed-0cf2-4c23-a75d-971f8607c2c5)

---

## 1. Executive Summary & Problem Scope

In transactional commerce, standard CRUD logic suffers catastrophic failure under concurrency: race conditions yield negative inventory, cart totals drift, duplicate charges occur without idempotency, and unauthenticated customers can snoop on peer orders.

Project 02 delivers a **production-grade, high-integrity E-Commerce Store (NovaMart)** architected to strictly eliminate overselling and financial race conditions. Powered by Django 5.2, Django REST Framework, PostgreSQL 18, and Next.js 14 (TypeScript + Tailwind CSS), this application implements:
1. **Concurrency-Safe Atomic Checkout:** Row-level locking (`select_for_update()`) in strict ascending product order wrapped in PostgreSQL ACID transactions (`transaction.atomic()`).
2. **Database-Level Defense:** A hard PostgreSQL `CHECK (stock >= 0)` constraint, preventing negative inventory even if an unhandled application bug were ever introduced.
3. **Price Freezing & Historical Integrity:** Order items capture and freeze `unit_price` at the instant of checkout, shielding order history from future product price alterations.
4. **Mock Payment Gateway with Idempotency:** Deterministic tokenized payment simulation (`tok_success` vs `tok_decline`) with unique idempotency keys, guaranteeing zero double charges and safe rollback.
5. **Stateful Order Lifecycle & Terminal FSM:** Finite state machine (`pending` -> `paid` -> `processing` -> `shipped` -> `delivered` / `cancelled`) with immutable terminal state enforcement (`delivered` orders cannot be illegally reverted).
6. **Industry-Standard Product Detail & Quick View Modal:** Complete item inspection with high-resolution photography, live warehouse availability badges, specifications, interactive quantity stepper (`−`/`+`), and direct "Buy Now" checkout.
7. **Hybrid Cart Engine:** Guest session cart (persistent `localStorage`) seamlessly transitioning to server-side authenticated cart on customer sign-in.
8. **Multi-User Persona Demonstration:** Instant navbar switching between Store Admin, Talha Ahmed (VIP Customer), Alice Buyer, Sara Shopper, and Guest Browsing mode.

---

## 2. Technology Stack & Local Host Environment

| Layer | Technology | Version | Purpose / Port |
| :--- | :--- | :--- | :--- |
| **Frontend** | Next.js / React / TypeScript | 14.2.35 / 18.3.1 / 5.x | Responsive Storefront UI (`http://127.0.0.1:3002`) |
| **Styling** | Tailwind CSS | 3.4.17 | Modern glassmorphism, responsive grid, dynamic badges |
| **Backend API** | Django / DRF | 5.2.x / 3.16.x | Domain logic, ACID checkout, RBAC (`http://127.0.0.1:8002`) |
| **Database** | PostgreSQL | 18 (x64 Windows) | ACID relational engine (`ecommerce_db`, port 5432) |
| **Authentication** | Django SimpleJWT | 5.5.x | Cryptographic HMAC-SHA256 Bearer tokens |
| **API Contract** | drf-spectacular | 0.29.x | OpenAPI 3.0 schema and Swagger/Redoc endpoints |
| **Testing** | pytest + pytest-django | 9.1.x / 4.14.x | Automated API test suite (15/15 passing tests) |
| **Deliverables** | ReportLab & XlsxWriter | 4.4.x / 3.2.x | Generated Vector PDFs and multi-tab financial models |

---

## 3. High-Integrity Engineering Architecture

```
[ Next.js 14 Storefront (Port 3002) ]
   ├── Store Catalog & 280ms Debounced Search
   ├── Product Detail / Quick View Modal (Quantity Stepper & Buy Now)
   ├── Sliding Cart Drawer (Guest LocalStorage & Authenticated Sync)
   ├── Concurrency Checkout Modal (tok_success / tok_decline Simulation)
   └── Order History & Admin Fulfillment Panel
         │ (REST / JSON + JWT Bearer)
         ▼
[ Django DRF API Layer (Port 8002) ]
   ├── Authentication & Role Middleware (Customer vs Admin)
   ├── Product Catalog & Filter ViewSet (/api/products/)
   ├── Multi-Quantity Cart API (/api/cart/add/, /update_quantity/)
   ├── Concurrency-Safe Checkout Service
   │     ├── transaction.atomic()
   │     ├── select_for_update() on Products (Ascending ID Order)
   │     ├── MockPaymentGateway (Idempotent)
   │     └── Order Creation + Price Snapshot
   └── Order Status State Machine (Terminal State Enforcement)
         │ (psycopg2 / Port 5432)
         ▼
[ PostgreSQL 18 Engine (ecommerce_db) ]
   ├── Hard CHECK Constraint (stock >= 0)
   ├── Unique Idempotency Keys on Payment Transactions
   └── Composite Indexes on (user_id, created_at DESC) & (sku)
```

---

## 4. Visual Architecture & Database ERD Diagrams

All diagrams required by the FalconXoft evaluation specification have been exported and provided in multiple formats for maximum defensibility. Clicking any preview diagram below will open the **live, editable Lucidchart workspace**:

### 4.1 System Architecture Diagram
[![System Architecture Diagram](02%20-%20architecture.png)](https://lucid.app/lucidchart/6ef90429-d6a5-4585-8b7f-2caaf728b0fc/edit?viewport_loc=-5287%2C321%2C16525%2C6279%2C0_0&invitationId=inv_9b2b97cf-501b-429e-993d-a24c927fa54c)
- **Vector PDF Deliverable:** [`02 - architecture.pdf`](02%20-%20architecture.pdf)
- **High-Res PNG Deliverable:** [`02 - architecture.png`](02%20-%20architecture.png)
- **Live Editable Lucidchart URL:** [Open Architecture in Lucidchart](https://lucid.app/lucidchart/6ef90429-d6a5-4585-8b7f-2caaf728b0fc/edit?viewport_loc=-5287%2C321%2C16525%2C6279%2C0_0&invitationId=inv_9b2b97cf-501b-429e-993d-a24c927fa54c)

---

### 4.2 Database ERD & Relational Schema
[![Database ERD Diagram](03%20-%20database-design.png)](https://lucid.app/lucidchart/fc2bb308-385a-44aa-8eec-6b89b42e11a7/edit?viewport_loc=-1034%2C-301%2C5760%2C2794%2C0_0&invitationId=inv_617b723e-1db7-444f-9378-4db505be3b4b)
- **Vector PDF Deliverable:** [`03 - database-design.pdf`](03%20-%20database-design.pdf)
- **High-Res PNG Deliverable:** [`03 - database-design.png`](03%20-%20database-design.png)
- **Live Editable Lucidchart ERD URL:** [Open Database ERD in Lucidchart](https://lucid.app/lucidchart/fc2bb308-385a-44aa-8eec-6b89b42e11a7/edit?viewport_loc=-1034%2C-301%2C5760%2C2794%2C0_0&invitationId=inv_617b723e-1db7-444f-9378-4db505be3b4b)
- **PostgreSQL 1-Click DDL:** [`schema.sql`](schema.sql)

---

### 4.3 API Workflows & Sequence Workflows
[![API Sequence Workflows](04%20-%20api-workflows.png)](https://lucid.app/lucidchart/1b0fe96e-3252-44ce-9d28-8ed2cf93e7d8/edit?view_items=vrvEd8gjuvU3&page=0_0&invitationId=inv_0f45dbed-0cf2-4c23-a75d-971f8607c2c5)
- **Vector PDF Deliverable:** [`04 - api-workflows.pdf`](04%20-%20api-workflows.pdf)
- **High-Res PNG Deliverable:** [`04 - api-workflows.png`](04%20-%20api-workflows.png)
- **Live Editable Lucidchart Sequence URL:** [Open API Workflows in Lucidchart](https://lucid.app/lucidchart/1b0fe96e-3252-44ce-9d28-8ed2cf93e7d8/edit?view_items=vrvEd8gjuvU3&page=0_0&invitationId=inv_0f45dbed-0cf2-4c23-a75d-971f8607c2c5)
- **Complete OpenAPI 3.0 Contract:** [`openapi.yaml`](openapi.yaml)

---

## 5. Quick Start & Execution Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 18 running locally on port 5432 with database `ecommerce_db` created

### Step 1: Backend Setup & Seeding
```powershell
# Navigate to backend directory
cd "d:\Weekend1_Talha Ahmed\02_Ecommerce\backend"

# Run database migrations
python manage.py migrate

# Seed catalog, test customers, and demo orders
python manage.py seed_data

# Launch backend API server
python manage.py runserver 8002
```
Backend will be live at `http://127.0.0.1:8002/api/`.  
OpenAPI Documentation: `http://127.0.0.1:8002/api/docs/`  
Raw OpenAPI YAML: `http://127.0.0.1:8002/api/schema/`

### Step 2: Frontend Setup & Launch
```powershell
# Navigate to frontend directory
cd "d:\Weekend1_Talha Ahmed\02_Ecommerce\frontend"

# Launch Next.js dev server on port 3002
npm run dev -- -p 3002
```
Frontend will be live at `http://127.0.0.1:3002/`.

---

## 6. Seed Credentials & User Personas

| Username | Password | Role | Pre-Seeded State & Testing Purpose |
| :--- | :--- | :--- | :--- |
| `admin` | `Admin@123` | `admin` | Store Admin: Full oversight of all 4 orders across platform; live stock replenishment controls. |
| `talha_customer` | `Customer@123` | `customer` | VIP Customer: Pre-seeded order `ORD-TALHA-001` ($279.00) + keyboard in cart. Isolated order view. |
| `alice_buyer` | `Password@123` | `customer` | Peer Customer: Pre-seeded order `ORD-ALICE-102` ($130.00) + keycap set in cart. |
| `sara_shopper` | `Customer@123` | `customer` | Isolated Customer: Pre-seeded order `ORD-D5D52C2C` ($65.00). Strict RBAC boundary check. |
| `Guest` | *(None)* | `guest` | Unauthenticated: Browses catalog, opens modal, adds to LocalStorage cart, prompts login at checkout. |

---

## 7. Automated Test Suite Verification

Run the comprehensive pytest suite verifying authentication, stock validation, checkout atomicity, race condition prevention, order isolation, and PostgreSQL check constraints:

```powershell
cd "d:\Weekend1_Talha Ahmed\02_Ecommerce\backend"
pytest tests/test_ecommerce_api.py -v
```

**Results:**
- Total Tests: **15**
- Passed: **15 (100%)**
- Execution Duration: ~69 seconds
- Verified Concurrency Test: `test_concurrency_race_condition_zero_negative_stock` (competing simultaneous threads strictly prevented from driving stock below zero).

---

## 8. Deliverables Index

Per Weekend Assignment §3, all 10 standard deliverables are provided:
1. `01 - README.md` — Project overview and setup instructions (this file)
2. `02 - architecture.pdf` — High-resolution landscape vector architecture diagram with editable Lucidchart link
3. `03 - database-design.pdf` — Relational ERD diagram, primary/foreign keys, check constraints, and 3NF analysis
4. `04 - api-workflows.pdf` — Sequence diagrams of checkout atomic workflow, race conditions, and FSM lifecycle
5. `05 - test-cases.xlsx` — 15 detailed test execution records with 10 required columns
6. `06 - engineering-decisions.md` — In-depth architectural trade-off analysis (including Docker exclusion rationale and FSM state machine)
7. `07 - source + demo/` — Complete runnable source code and verified demo script
8. `08 - cost-and-scaling.xlsx` — Hostinger VPS vs AWS comparison and 100 to 1M user scaling roadmap
9. `09 - sources-and-disclosure.md` — Complete honesty and AI assistance disclosures
10. `10 - submission-index.md` — Traceability index linking requirements to code and artifacts
11. `LUCIDCHART_DIAGRAMS_CODE.md` — Exact Mermaid & SQL diagram definitions for 1-click import into Lucidchart
12. `ECOMMERCE_TESTING_AND_VIVA_GUIDE.md` — Comprehensive bilingual browser testing and viva defense walkthrough
