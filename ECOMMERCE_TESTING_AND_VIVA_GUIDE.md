# FALCONXOFT WEEKEND 1 — E-COMMERCE STORE MVP
## Complete Browser Testing & Viva Defense Guide (Roman Urdu & English)

**Author:** Talha Ahmed  
**Project:** 02_Ecommerce (High-Integrity E-Commerce Store — NovaMart)  
**Frontend URL:** `http://localhost:3002`  
**Backend API URL:** `http://127.0.0.1:8002/api/`  
**Database:** PostgreSQL 18 (`ecommerce_db`)  
**Live Editable Lucidchart Link:** [Lucidchart Workspace](https://lucid.app/lucidchart/6ef90429-d6a5-4585-8b7f-2caaf728b0fc/edit?invitationId=inv_9b2b97cf-501b-429e-993d-a24c927fa54c&page=yofE0ycUHjJN#)

---

## 1. Task Background — Aapko Task Kya Mila Tha? (Requirements Overview)

FalconXoft Weekend 1 assessment ka doosra project tha ek **High-Integrity E-Commerce Store MVP** banana.

Commerce applications mein sabse barha masla hota hai **Concurrency Race Conditions** aur **Financial Inconsistencies**:
- Agar stock sirf 1 bacha ho aur 2 buyers ek sath "Pay Now" click karein, to aam applications mein stock negative (-1) ho jata hai aur company ko financial loss hota hai (Overselling).
- Agar agle hafte kisi product ki price $100 se barh kar $150 ho jaye, to purane orders ki total amount corrupt ho jati hai agar price snapshot na liya jaye (Price Drift).
- Agar buyer double-click kar de to do dafa paise kat jate hain (Duplicate Charges).

HR requirement sheet ke mutabiq humne ek **zero-defect transactional commerce system** banaya hai jisme:
1. **Product Catalog & Stock Control:** Live stock tracking with stock availability indicators.
2. **Product Detail & Quick View Modal:** Complete item inspection with high-resolution photography, live warehouse availability badges, specifications, interactive quantity stepper (`−`/`+`), and direct "Buy Now" checkout.
3. **Hybrid Cart:** Session (`localStorage`) aur database-backed cart jo live inventory ke sath sync rehta hai.
4. **Concurrency-Safe Atomic Checkout:** Row-level locking (`select_for_update()`) PostgreSQL transactions ke andar taake negative inventory 100% impossible ho.
5. **Database-Level Defense:** PostgreSQL par hard `CHECK (stock >= 0)` constraint.
6. **Mock Payment Gateway with Idempotency:** Deterministic payment tokens (`tok_success` vs `tok_decline`) jo real payment gateways (jaise Stripe) ki tarah act karta hai.
7. **Immutable Price Snapshots:** Order create hote waqt `unit_price` freeze ho jata hai.
8. **Order State Machine & Terminal State Enforcement:** `pending` ➔ `paid` ➔ `processing` ➔ `shipped` ➔ `delivered` (terminal) / `cancelled`.
9. **Customer Privacy Isolation:** Ek customer doosre customer ke orders nahi dekh sakta (HTTP 404).
10. **Zero Docker Constraint:** Pure bare-metal execution (Python 3.11 + Next.js 14 + PostgreSQL 18).

---

## 2. Humne Kya Aur Kaise Banaya? (Architecture & Technical Decisions)

### Tech Stack:
- **Backend:** Python 3.11 + **Django 5.2** + **Django REST Framework (DRF)**.
  - Concurrency Locking: `select_for_update()` in deterministic sorted ID order (Deadlock prevention).
  - Transaction Atomicity: `transaction.atomic()`.
  - JWT Authentication: `djangorestframework-simplejwt`.
  - API Documentation: `drf-spectacular` (OpenAPI 3.0 / Swagger schema).
- **Frontend:** **Next.js 14** (App Router, React 18, TypeScript) + **Tailwind CSS**.
  - Modern shopping interface, 280ms debounced search, product detail modal with quantity stepper, live cart drawer, checkout modal, order status tracking.
  - Built-in **1-Click Demo Switcher** navbar mein (Store Admin, Talha Ahmed, Alice Buyer, Sara Shopper, Guest).
- **Database:** **PostgreSQL 18** (`ecommerce_db`) ACID relational engine.
- **Testing:** `pytest` + `pytest-django` ke **15 automated test cases** (100% pass rate in ~69s).

---

## 3. Demo Accounts & Login Credentials

Frontend navbar ke top-right par **"Demo Switch"** buttons diye gaye hain. Credentials yeh hain:

| Role | Username | Password | Pre-Seeded State & Purpose |
| :--- | :--- | :--- | :--- |
| 👑 **Store Admin** | `admin` | `Admin@123` | **Full Store Management:** Sabhi customers ke orders dekh sakta hai, order status transition kar sakta hai, inventory adjust kar sakta hai. |
| 🛒 **Talha Ahmed** | `talha_customer` | `Customer@123` | **VIP Customer:** Pre-seeded order `ORD-TALHA-001` ($279.00) + keyboard cart. Isolated private order history. |
| 🛒 **Alice Buyer** | `alice_buyer` | `Password@123` | **Alternative Customer:** Pre-seeded order `ORD-ALICE-102` ($130.00) + keycap cart. |
| 👥 **Sara Shopper** | `sara_shopper` | `Customer@123` | **Peer Customer:** Pre-seeded order `ORD-D5D52C2C` ($65.00). Strict RBAC boundary check. |
| 👀 **Guest Shopper** | *(None)* | N/A | **Unauthenticated Shopper:** LocalStorage guest cart, modal inspection, and login prompt on checkout. |

---

## 4. Browser Testing Walkthrough — Step-by-Step Test Kaise Karein?

Dono servers already aapke terminal mein chal rahe hain:
- **Backend API:** `http://127.0.0.1:8002`
- **Frontend Store:** `http://localhost:3002`

Apne browser mein **`http://localhost:3002`** open karein aur yeh steps perform karein:

### Step 1: Browse Catalog & Test Product Detail / Quick View Modal
1. Browser mein `http://localhost:3002` kholein.
2. Catalog mein 6 seeded electronics & accessories products nazar aayenge.
3. Kisi bhi product card ki image, title, ya **`[ 👁️ Details ]`** button par click karein!
4. **Result:**
   - Beautiful 2-column **Product Detail Modal** open hoga.
   - Left side: High-resolution picture, SKU badge, live stock status pill, aur 3 trust badges (Priority Cargo, Authentic, ACID Safe).
   - Right side: Full specifications, warehouse stock status banner, bold price ($999.00) with free shipping tag.
   - **Interactive Quantity Stepper:** `+` aur `−` dabakar quantity adjust karein (e.g. 2). Subtotal automatically `$1998.00` calculate ho jayega!
   - Click karein **`[ 🛒 Add to Cart (2) ]`** ya direct **`[ ⚡ Buy Now ]`**!

### Step 2: Test Guest Cart Persistence (Session Cart)
1. Logout / Guest mode mein rehte hue 1-2 items cart mein add karein.
2. Cart Drawer open karein:
   - Items display honge subtotal ke sath.
   - Bottom par notification banner aayega: `Items saved in guest cart! To checkout and reserve stock, choose an account: [As Talha] [As Alice]`.
3. Page refresh karein: items cart mein bilkul mehfooz rahenge (`localStorage` durability).

### Step 3: Switch to Talha Ahmed (VIP Customer) & Checkout
1. Navbar se **"🛒 Customer: Talha"** button par click karein.
2. Toast message aayega: `Switched account to @talha_customer (CUSTOMER)`.
3. Top navigation tabs check karein:
   - **`[ 🛍️ Store Catalog (6 Items) ]`**: Hamesha catalog par wapas laata hai.
   - **`[ 📦 Orders (1) ]`**: Talha ke orders dikhata hai.
4. Cart drawer open karein aur **"Proceed to Checkout"** click karein.
5. Checkout Modal mein:
   - Select karein: **`Approved Card (tok_success)`** (Green button).
   - Click karein **"Pay & Place Order"**.
6. **Result:**
   - Order instant `PAID` ho jayega.
   - Database mein stock atomic decrement ho jayega.
   - Screen automatically **Orders** view par switch ho jayegi jahan naya order price-frozen receipt ke sath display hoga.

### Step 4: Test Payment Decline & Concurrency Rollback (`tok_decline`)
1. Catalog par wapas aayein aur koi item cart mein add karein.
2. Checkout modal mein is baar **`Declined Card (tok_decline)`** (Red button) select karein aur Pay dabayein.
3. **Result:**
   - Screen par high-priority error alert aayega: `Payment was declined by card issuer (tok_decline simulated failure). Stock and cart remain intact.`
   - Stock bilkul deduct **NAHI** hoga!
   - Cart items preserve rahenge.

### Step 5: Test Cross-Customer Order Isolation (Viva Essential!)
1. Top bar se **"🛒 Alice Buyer"** par click karein.
2. Orders tab mein jayein: Alice ko sirf apna order `ORD-ALICE-102` nazar aayega. Talha ka order `ORD-TALHA-001` bilkul nazar **NAHI** aayega!
3. Ab **"👥 Sara Shopper"** switch karein: Sara ko sirf `ORD-D5D52C2C` nazar aayega.
4. Yeh prove karta hai ke Django ViewSet mein strict `filter(user=request.user)` enforced hai aur IDOR (Insecure Direct Object Reference) 100% prevented hai.

### Step 6: Test Admin Order Fulfillment & Terminal State Protection
1. Navbar se **"👑 Admin"** par click karein.
2. Admin Dashboard open hoga jisme platform ke **tamam 4 orders** nazar aayenge (Talha, Alice, Sara).
3. Status transition dropdown use karke order ko `PAID` ➔ `PROCESSING` ➔ `SHIPPED` ➔ `DELIVERED` karein.
4. **Notice:** Jab order `DELIVERED` ho jata hai:
   - Dropdown automatic lock ho jata hai aur badge dikhata hai: **`🔒 Terminal State (DELIVERED)`**.
   - Delivered order ko revert karne ki koshish API par `HTTP 400 Bad Request` se reject hoti hai.

---

## 5. Viva Questions & Model Answers (Oral Defense)

### Q1: Concurrency issue kaise solve kiya? Agar 2 log aakhri product ek sath buy karein?
> **Answer:** "Humne Django ORM ka `select_for_update()` use kiya hai jo PostgreSQL engine par row-level pessimistic lock acquire karta hai inside `transaction.atomic()`. Thread A row lock karta hai, stock check karta hai, decrement karta hai aur commit karta hai. Tab tak Thread B wait karti hai. Jab Thread B ko row milti hai to stock 0 ho chuka hota hai aur system cleanly `HTTP 409 Conflict` throw karta hai. Mazeed defense-in-depth ke liye humne database table par hard `CHECK (stock >= 0)` constraint lagaya hai taake engine level par negative stock impossible ho."

### Q2: Deadlock prevention kaise hoti hai agar multi-item cart ho?
> **Answer:** "Agar Customer A cart mein Product 1 aur 2 buy kar raha ho aur Customer B Product 2 aur 1 buy kar raha ho, to naive locking se deadlock aa sakta hai. Humne `services.py` mein locking se pehle product IDs ko ascending order (`product_ids.sort()`) mein sort kiya hai. Dono threads hamesha identical sequence mein lock acquire karti hain, mathematically eliminating circular wait condition."

### Q3: OrderItem mein unit_price alag se kyu store ki hai? Product table se direct kyu nahi li?
> **Answer:** "Yeh audit integrity aur financial compliance ke liye mandatory hai. Agar merchant product ki price $100 se barha kar $200 kar de, to purane customers ke past orders corrupt ho jayenge agar price freeze na ki jaye. Hum order placement ke instant par active price ka snapshot `OrderItem.unit_price` mein freeze kar dete hain."

### Q4: Payment gateway real kyu nahi lagaya?
> **Answer:** "Real gateways (Stripe/Paypal) external network latency, secret keys, aur sandbox rate limits create karte hain jo CI/CD automated tests ko flaky banate hain. Humne industry-standard deterministic `MockPaymentGateway` implement kiya hai jo `tok_success` aur `tok_decline` tokens accept karta hai with unique idempotency keys, identical to Stripe's PaymentIntent architecture."
