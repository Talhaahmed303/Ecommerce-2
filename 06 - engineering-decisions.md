# FALCONXOFT WEEKEND 1 EVALUATION — PROJECT 02: ENGINEERING DECISIONS & TRADE-OFFS

**Author:** Talha Ahmed  
**Evaluation Role:** Full-Stack Intern Performance Evaluation (Weekend 1)  
**Deliverable Number:** 06 of 10  
**Specification Reference:** Weekend Assignment.pdf §3  

---

## 1. Decision 1: Direct Host Execution vs Docker / Docker Compose

### Context & Constraint
The project requirements evaluate runnable code, system architecture, and local reproducibility. A key engineering directive was specified: **execute directly on the bare-metal host environment with zero Docker or Docker Compose containers**.

### Alternatives Considered
1. **Docker & Docker Compose:** Containerize Next.js, Django, and PostgreSQL into multi-container network.
2. **Direct Bare-Metal Host Execution (Adopted):** Run Django DRF on Python 3.11 with virtual environments, Next.js on Node.js 18+, and connect directly to the native PostgreSQL 18 Windows service (`postgresql-x64-18`).

### Trade-Off Evaluation

| Evaluation Criteria | Docker / Docker Compose | Bare-Metal Host Execution (Adopted) |
| :--- | :--- | :--- |
| **Windows Overhead & Resource Consumption** | High (WSL2 VM consumes 4-8 GB RAM, high disk I/O latency on `/mnt/d`) | Minimal (Zero virtualization overhead, direct NVMe disk speed) |
| **Startup & Debugging Speed** | Slower container build cycles, hidden log layers | Instant startup (`python manage.py runserver`, `npm run dev`) with instant hot-reload |
| **Local Environment Reproducibility** | High across heterogeneous OS environments | High when documented with explicit package versions and scripts |
| **Production Parity** | High container parity with cloud ECS/K8s | Requires container build step during deployment phase |

### Rationale & Production Migration Path
For this intensive weekend evaluation on Windows 11, running natively eliminates virtualization overhead, prevents WSL2 file-watcher latency issues in Next.js, and allows direct inspection of PostgreSQL via standard tools (`psql`, pgAdmin). In `06 - engineering-decisions.md` and `08 - cost-and-scaling.xlsx`, we detail the containerization path for AWS ECS / Fargate when transitioning from MVP to cloud scale.

---

## 2. Decision 2: Concurrency Control Strategy for Stock Allocation

### Context
When multiple shoppers attempt to checkout the last remaining units of inventory simultaneously, naive CRUD logic executes two read operations (`SELECT stock FROM products`), sees stock available, and writes two decrement operations (`UPDATE products SET stock = stock - qty`), yielding negative inventory.

### Alternatives Considered
1. **Optimistic Concurrency Control (OCC):** Add a `version` integer column. On update: `UPDATE products SET stock = stock - qty, version = version + 1 WHERE id = x AND version = old_version`. If affected rows == 0, abort and retry.
2. **Redis Distributed Locks (Redlock):** Acquire lock on key `lock:product:{id}` before DB query; release lock after commit.
3. **Pessimistic Row-Level Locking (`select_for_update()`) with Ordered Acquisition (Adopted):** Lock product rows inside `transaction.atomic()` using `select_for_update()` in ascending product ID order.

### Trade-Off Evaluation

| Criteria | Optimistic Concurrency Control | Distributed Redis Lock | Pessimistic `select_for_update()` (Adopted) |
| :--- | :--- | :--- | :--- |
| **Implementation Complexity** | Medium (Requires retry loop & backoff logic) | High (Requires Redis cluster, TTL management, failure recovery) | Low/Medium (Native PostgreSQL feature, zero additional infrastructure) |
| **High Contention Behavior** | High failure/retry rates during flash sales | Good, but lock leak risk if process crashes | Serializes transactions cleanly; winner commits, loser fails cleanly |
| **Deadlock Prevention** | Inherently deadlock-free | Potential deadlock if multi-item lock order is unmanaged | Guaranteed deadlock-free when sorting product IDs before locking (`order_by('id')`) |
| **Transactional Guarantees** | Application-level check | Out-of-band lock; DB could still abort independently | Pure ACID transaction; lock releases automatically on commit or rollback |

### Rationale
Pessimistic row-level locking via PostgreSQL is the gold standard for high-integrity financial transactions. By sorting product IDs before invoking `select_for_update()`, we mathematically eliminate deadlocks. This is proven in our automated test `test_concurrency_race_condition_zero_negative_stock`.

---

## 3. Decision 3: PostgreSQL Check Constraint as Defense-in-Depth

### Context
Even with robust application-level locking, human error or future refactorings (e.g. background job, third-party integration, direct SQL script) could bypass the Python service layer.

### Solution Adopted
We enacted a database-level hard constraint in the Django model:
```python
class Meta:
    constraints = [
        models.CheckConstraint(
            check=models.Q(stock__gte=0),
            name="check_stock_non_negative"
        )
    ]
```

### Rationale
Defense-in-depth is mandatory for high-integrity financial systems. If any query or thread ever attempts to drive `stock < 0`, PostgreSQL's relational engine raises `IntegrityError (check violation)`, immediately rolling back the transaction. This was verified in automated test `test_stock_negative_check_constraint`.

---

## 4. Decision 4: Unit Price Freezing at Checkout

### Problem Scope
A naive e-commerce design links `OrderItem` directly to `Product.price`. If a merchant subsequently raises a laptop price from $999 to $1,299, historical order receipts, customer invoices, and financial ledger reports would retroactively display inflated totals.

### Solution Adopted
Every `OrderItem` includes an immutable `unit_price = models.DecimalField(max_digits=10, decimal_places=2)`. During `checkout_cart()`, the active product price is copied into `OrderItem.unit_price`.

### Trade-Offs
- **Storage:** Redundant storage of 8 bytes per order item.
- **Integrity Gain:** 100% legal and accounting compliance; orders remain perfectly audit-proof regardless of subsequent catalog updates.

---

## 5. Decision 5: Deterministic Mock Payment Gateway Architecture

### Context
Real payment gateways (Stripe, Adyen) require external network calls, secret keys, and webhook endpoints, introducing non-deterministic network latency, rate limits, and flaky failures in local automated test suites.

### Solution Adopted
A dedicated `MockPaymentGateway` abstraction with deterministic test tokens:
- `tok_success`: Simulates successful authorization and settlement (`status = 's'`).
- `tok_decline`: Simulates card rejection or insufficient funds (`status = 'f'`).
- **Idempotency Key:** Every transaction generates and requires a unique idempotency key. Repeating a checkout with an identical key returns the cached payment record rather than re-executing.

### Rationale
This architecture allows full end-to-end testing of both success and rollback paths without external dependencies, while maintaining identical interfaces to Stripe's Python SDK (`stripe.PaymentIntent.create`).

---

---

## 6. Decision 6: Product Detail Quick-View Modal vs Dedicated Multi-Page Route

### Context & User Need
In high-velocity consumer electronics stores, shoppers frequently compare specifications (refresh rate, USB-C power delivery, key switch profiles) across multiple items before committing to a purchase. Requiring a full browser page navigation (`/products/[id]`) introduces navigation latency, resets scroll positions, and disrupts browsing rhythm.

### Alternatives Considered
1. **Dedicated SSR Page Route (`/products/[id]`):** Traditional server-side rendered product page.
2. **Inline Expandable Accordion:** Expand card in place on the catalog grid.
3. **High-Performance Quick-View Modal (Adopted):** Client-side modal overlay with high-resolution media zoom, real-time stock alert banners, live quantity stepper (`−`/`+`), dynamic subtotal calculations, and 1-click "Buy Now" checkout.

### Trade-Off Evaluation
- **Pros of Quick-View Modal:** Zero page reload latency; preserves user scroll and category filter state; supports instant comparison; immediate transition to cart drawer or checkout drawer.
- **Cons & Mitigation:** Deep-link bookmarking requires query parameters. In a future iteration, we sync modal state with shallow URL routing (`?product=sku-123`) without server roundtrips.

---

## 7. Decision 7: Order Finite State Machine (FSM) & Immutable Terminal State Enforcement

### Context
Order lifecycles must follow strict business domain rules. If an order has been delivered to a customer's physical doorstep, allowing an admin or rogue API call to regress its status to "processing" creates massive shipping and financial reconciliation chaos.

### Solution Adopted
We implemented a strict, deterministic transition matrix in `backend/apps/orders/models.py` and `views.py`:
- `pending` ➔ `paid` or `cancelled`
- `paid` ➔ `processing` or `cancelled`
- `processing` ➔ `shipped` or `cancelled`
- `shipped` ➔ `delivered`
- `delivered` ➔ **TERMINAL STATE (No further transitions permitted)**
- `cancelled` ➔ **TERMINAL STATE (No further transitions permitted)**

Any attempt to update a delivered order returns `HTTP 400 Bad Request: "Invalid status transition from 'delivered' to '...' Delivered orders are immutable."` The frontend UI reflects this by rendering `🔒 Terminal State (DELIVERED)` and disabling further mutations.

---

## 8. Decision 8: Hybrid Guest vs Authenticated Cart Persistence

### Context
First-time shoppers often add products to their cart before deciding to register or log in. Requiring mandatory upfront authentication increases cart abandonment by up to 35%.

### Solution Adopted
We engineered a hybrid dual-layer cart engine:
1. **Guest Mode:** Cart state is managed in client-side persistent `localStorage` (`guest_cart`). Guests can view real-time subtotal, adjust quantities, inspect stock availability, and view the sliding cart drawer without an account.
2. **Authenticated Transition:** When the user clicks "Proceed to Checkout" or selects a customer profile (Talha or Alice), the system prompts authentication and syncs the session items to the PostgreSQL database-backed cart (`/api/cart/add/`).

---

## 9. Summary of Architectural Posture

| Component | Choice | Core Benefit |
| :--- | :--- | :--- |
| **Host Runtime** | Bare-Metal Windows Local Host | Peak developer velocity, zero virtualization friction, explicit reproducibility |
| **Concurrency Guard** | `select_for_update()` + Ordered Keys | Strict zero overselling, zero deadlocks |
| **Integrity Guard** | PostgreSQL `CHECK (stock >= 0)` | Defense-in-depth at engine layer |
| **Ledger Guard** | Frozen `unit_price` in OrderItem | Immutable historical audit compliance |
| **Payment Simulation** | Deterministic Tokenized Gateway | Instant, 100% reproducible test verification |
| **UX & Product View** | Quick-View Modal with Qty Stepper | Fast item inspection, zero scroll loss, instant checkout |
| **Order Lifecycle** | Enforced FSM with Terminal States | Immutable delivered state; prevents illegal regressions |
| **Cart Persistence** | Hybrid LocalStorage & PostgreSQL | Low friction for guests; full durability for customers |
