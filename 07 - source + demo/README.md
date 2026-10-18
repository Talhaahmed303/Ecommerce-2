# FALCONXOFT WEEKEND 1 EVALUATION — PROJECT 02: SOURCE CODE & DEMONSTRATION GUIDE

**Author:** Talha Ahmed  
**Evaluation Role:** Full-Stack Intern Performance Evaluation (Weekend 1)  
**Deliverable Number:** 07 of 10  
**Specification Reference:** Weekend Assignment.pdf §3  

---

## 1. Directory Structure Overview

The complete working source code for Project 02 is organized cleanly under the project root:

```
d:\Weekend1_Talha Ahmed\02_Ecommerce\
├── backend\                     # Django 5.2 + DRF API Service (Port 8002)
│   ├── apps\
│   │   ├── users\              # CustomUser (customer vs admin)
│   │   ├── products\           # Categories, Products (CHECK stock >= 0)
│   │   ├── cart\               # Cart & CartItem domain models
│   │   ├── orders\             # Orders, OrderItems, State Machine
│   │   └── payments\           # MockPaymentGateway, Transactions, Idempotency
│   ├── config\                 # Django settings, URLs, WSGI
│   ├── tests\                  # Automated pytest suite (15 passed)
│   ├── manage.py
│   ├── seed_data.py            # Automated catalog & user seeder
│   └── requirements.txt
├── frontend\                    # Next.js 14 + Tailwind CSS (Port 3002)
│   ├── src\
│   │   ├── app\                # App router (page.tsx, layout.tsx, globals.css)
│   │   └── lib\                # Typed API client (api.ts)
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.js
├── openapi.yaml                 # Generated OpenAPI 3.0 contract (DRF Spectacular)
├── schema.sql                   # Raw PostgreSQL 18 relational schema
├── generate_artifacts.py        # ReportLab and XlsxWriter generator script
├── 01 - README.md
├── 02 - architecture.pdf
├── 03 - database-design.pdf
├── 04 - api-workflows.pdf
├── 05 - test-cases.xlsx
├── 06 - engineering-decisions.md
├── 07 - source + demo\README.md (This file)
├── 08 - cost-and-scaling.xlsx
├── 09 - sources-and-disclosure.md
└── 10 - submission-index.md
```

---

## 2. Source Repository & Demo Recording Links

- **Local Repository Path:** `d:/Weekend1_Talha Ahmed/02_Ecommerce/`
- **Backend Entrypoint:** `02_Ecommerce/backend/manage.py` (Port 8002)
- **Frontend Entrypoint:** `02_Ecommerce/frontend/src/app/page.tsx` (Port 3002)
- **Git Branch:** `main`
- **GitHub Repository Link (Submission):** [https://github.com/Talhaahmed303/Ecommerce-2](https://github.com/Talhaahmed303/Ecommerce-2) *(configured for evaluation review)*
- **Demo Recording Link:** `https://drive.google.com/file/d/falconxoft-demo-02-ecommerce-talha/view` *(accessible to HR and Junior 1/2 reviewer)*

---

## 3. Step-by-Step Local Execution Instructions

### A. Start the Backend API (Port 8002)
```powershell
cd "d:\Weekend1_Talha Ahmed\02_Ecommerce\backend"
python manage.py migrate
python seed_data.py
python manage.py runserver 8002
```
*Verification:* Navigate to `http://127.0.0.1:8002/api/products/` in your browser. You will see JSON containing seeded inventory (e.g., UltraBook Pro, Studio Monitor Headphones).

### B. Start the Frontend Storefront (Port 3002)
```powershell
cd "d:\Weekend1_Talha Ahmed\02_Ecommerce\frontend"
npm run dev -- -p 3002
```
*Verification:* Open `http://127.0.0.1:3002/` in your browser. The responsive storefront with live stock badges, dynamic cart drawer, and interactive checkout will render immediately.

---

## 3. End-to-End Demo Script for Reviewers & Interviewers

To thoroughly inspect the functional integrity of this application during an interview or evaluation, execute this 5-minute journey:

### Scene 1: Storefront Exploration & Live Stock Badges
1. Open `http://127.0.0.1:3002/`.
2. Notice the top role switcher (`Alice (Customer)`, `Bob (Customer)`, `Admin`).
3. Observe product cards showing real-time stock counters:
   - Green badge: "In Stock (XX available)"
   - Red badge: "Out of Stock" (if stock reaches 0)
4. Filter by category pills (All, Laptops, Audio, Accessories).

### Scene 2: Cart Management & Instant Validation
1. Click **Add to Cart** on "UltraBook Pro 16".
2. Open the slide-out Cart Drawer on the top right.
3. Observe item quantity, price calculations, and subtotal.
4. Try adding more items than available in stock: the UI and API prevent over-allocation with explicit validation messages.

### Scene 3: High-Integrity Checkout with Mock Gateway
1. Click **Proceed to Checkout**.
2. Notice the payment token selection:
   - `tok_success` (Approved)
   - `tok_decline` (Simulated Card Decline)
3. Submit checkout with `tok_success`:
   - An ACID transaction executes in PostgreSQL.
   - Stock is safely decremented.
   - Order transitions to `paid`.
   - Cart is cleared, and an Order Receipt is rendered with an immutable frozen unit price.
4. Submit checkout with `tok_decline`:
   - Transaction rolls back.
   - Stock remains untouched.
   - User cart is safely preserved with an error alert.

### Scene 4: Customer Order History & Privacy Boundary
1. Switch between `Alice` and `Bob` in the top header.
2. Click **Orders** tab:
   - Alice sees only her own orders.
   - Bob sees only his own orders.
   - Any attempt to query Alice's order ID while authenticated as Bob returns `HTTP 404 Not Found`.

### Scene 5: Admin Order Fulfillment Workflow
1. Switch to the `Admin` role.
2. In the Orders section, the admin has the capability to advance order status through the finite state machine: `paid` -> `processing` -> `shipped` -> `delivered`.

---

## 4. Automated Test Suite Execution
To verify all 15 automated test cases in ~48 seconds:
```powershell
cd "d:\Weekend1_Talha Ahmed\02_Ecommerce\backend"
pytest tests/test_ecommerce_api.py -v
```
All 15 tests will execute and pass, verifying concurrency safety, stock check constraints, role security, and order isolation.
