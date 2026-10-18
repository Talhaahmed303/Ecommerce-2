# FALCONXOFT WEEKEND 1 EVALUATION — PROJECT 02: SUBMISSION INDEX & TRACEABILITY

**Author:** Talha Ahmed  
**Evaluation Role:** Full-Stack Intern Performance Evaluation (Weekend 1)  
**Deliverable Number:** 10 of 10  
**Specification Reference:** Weekend Assignment.pdf §3  
**Status:** 100% Complete & Verified  
**GitHub Repository:** [https://github.com/Talhaahmed303/Ecommerce-2](https://github.com/Talhaahmed303/Ecommerce-2)  
**Live Editable Architecture:** [Open Architecture in Lucidchart](https://lucid.app/lucidchart/6ef90429-d6a5-4585-8b7f-2caaf728b0fc/edit?viewport_loc=-5287%2C321%2C16525%2C6279%2C0_0&invitationId=inv_9b2b97cf-501b-429e-993d-a24c927fa54c)  
**Live Editable Database ERD:** [Open Database ERD in Lucidchart](https://lucid.app/lucidchart/fc2bb308-385a-44aa-8eec-6b89b42e11a7/edit?viewport_loc=-1034%2C-301%2C5760%2C2794%2C0_0&invitationId=inv_617b723e-1db7-444f-9378-4db505be3b4b)  
**Live Editable API Workflows Sequence:** [Open API Workflows in Lucidchart](https://lucid.app/lucidchart/1b0fe96e-3252-44ce-9d28-8ed2cf93e7d8/edit?view_items=vrvEd8gjuvU3&page=0_0&invitationId=inv_0f45dbed-0cf2-4c23-a75d-971f8607c2c5)

---

## 1. Master Requirements Traceability Matrix (Project 02)

| Requirement ID | Requirement Description | Implementation Location | Test Case Evidence | Deliverable Ref |
| :--- | :--- | :--- | :--- | :--- |
| **REQ-ECOM-01** | User authentication with Customer and Admin roles | `backend/apps/users/` | `TC-ECOM-AUTH-01`, `TC-ECOM-AUTH-02` | `01 - README.md` |
| **REQ-ECOM-02** | Product catalog with categories, stock levels, and active filter | `backend/apps/products/` | `TC-ECOM-CAT-01` | `03 - database-design.pdf` |
| **REQ-ECOM-03** | Shopping cart with stock validation and itemized subtotal | `backend/apps/cart/` | `TC-ECOM-CART-01`, `TC-ECOM-CART-02` | `04 - api-workflows.pdf` |
| **REQ-ECOM-04** | Concurrency-safe atomic checkout preventing overselling | `backend/apps/orders/services.py` | `TC-ECOM-CHK-01`, `TC-ECOM-CON-01` | `06 - engineering-decisions.md` |
| **REQ-ECOM-05** | Database-level non-negative stock check constraint | `backend/apps/products/models.py` | `TC-ECOM-CHK-04`, `schema.sql` | `03 - database-design.pdf`, `schema.sql` |
| **REQ-ECOM-06** | Mock payment gateway with idempotency and decline handling | `backend/apps/payments/` | `TC-ECOM-CHK-01`, `TC-ECOM-CHK-03` | `04 - api-workflows.pdf` |
| **REQ-ECOM-07** | Frozen unit price capture in OrderItem | `backend/apps/orders/models.py` | `TC-ECOM-ORD-05` | `03 - database-design.pdf` |
| **REQ-ECOM-08** | Customer order history with cross-customer data isolation | `backend/apps/orders/views.py` | `TC-ECOM-ORD-01` | `05 - test-cases.xlsx` |
| **REQ-ECOM-09** | Admin order fulfillment status workflow | `backend/apps/orders/views.py` | `TC-ECOM-ORD-03`, `TC-ECOM-ORD-04` | `01 - README.md` |
| **REQ-ECOM-10** | Modern Next.js 14 frontend with dynamic cart & stock badges | `frontend/src/app/page.tsx` | Verified with live browser automated test | `07 - source + demo/` |
| **REQ-ECOM-11** | Industry-Standard Product Detail / Quick View Modal | `frontend/src/app/page.tsx` | Interactive quantity stepper (`−`/`+`), specs, Buy Now | `06 - engineering-decisions.md` |
| **REQ-ECOM-12** | Hybrid Guest to Authenticated Cart Transition | `frontend/src/app/page.tsx` | LocalStorage session cart with seamless sign-in sync | `06 - engineering-decisions.md` |
| **REQ-ECOM-13** | FSM Terminal State Immutability Enforcement | `backend/apps/orders/serializers.py` | `TC-ECOM-ORD-04` (rejects invalid transitions from delivered) | `06 - engineering-decisions.md` |

---

## 2. Deliverables Checklist & File Inventory

| Deliverable Name | File Type | File Path | Status | Verification Check |
| :--- | :--- | :--- | :--- | :--- |
| **01 - README.md** | Markdown | `02_Ecommerce/01 - README.md` | COMPLETE | Setup commands, roles, and architecture verified |
| **02 - architecture.pdf** | Vector PDF | `02_Ecommerce/02 - architecture.pdf` | COMPLETE | [Open Architecture in Lucidchart](https://lucid.app/lucidchart/6ef90429-d6a5-4585-8b7f-2caaf728b0fc/edit?viewport_loc=-5287%2C321%2C16525%2C6279%2C0_0&invitationId=inv_9b2b97cf-501b-429e-993d-a24c927fa54c) |
| **03 - database-design.pdf** | Vector PDF | `02_Ecommerce/03 - database-design.pdf` | COMPLETE | [Open Database ERD in Lucidchart](https://lucid.app/lucidchart/fc2bb308-385a-44aa-8eec-6b89b42e11a7/edit?viewport_loc=-1034%2C-301%2C5760%2C2794%2C0_0&invitationId=inv_617b723e-1db7-444f-9378-4db505be3b4b) |
| **04 - api-workflows.pdf** | Vector PDF | `02_Ecommerce/04 - api-workflows.pdf` | COMPLETE | [Open API Workflows in Lucidchart](https://lucid.app/lucidchart/1b0fe96e-3252-44ce-9d28-8ed2cf93e7d8/edit?view_items=vrvEd8gjuvU3&page=0_0&invitationId=inv_0f45dbed-0cf2-4c23-a75d-971f8607c2c5) |
| **05 - test-cases.xlsx** | Formatted Excel | `02_Ecommerce/05 - test-cases.xlsx` | COMPLETE | 15 real test records matching `test_ecommerce_api.py` |
| **06 - engineering-decisions.md** | Markdown | `02_Ecommerce/06 - engineering-decisions.md` | COMPLETE | 8 deep architectural decisions & trade-offs |
| **07 - source + demo/** | Directory | `02_Ecommerce/07 - source + demo/README.md` | COMPLETE | [GitHub: Talhaahmed303/Ecommerce-2](https://github.com/Talhaahmed303/Ecommerce-2) |
| **08 - cost-and-scaling.xlsx** | Formatted Excel | `02_Ecommerce/08 - cost-and-scaling.xlsx` | COMPLETE | Hostinger VPS vs AWS + 100 to 1M user models |
| **09 - sources-and-disclosure.md** | Markdown | `02_Ecommerce/09 - sources-and-disclosure.md` | COMPLETE | Honest citations & AI assistance statement |
| **10 - submission-index.md** | Markdown | `02_Ecommerce/10 - submission-index.md` | COMPLETE | Traceability matrix and file inventory (this file) |
| **LUCIDCHART_DIAGRAMS_CODE.md** | Markdown | `02_Ecommerce/LUCIDCHART_DIAGRAMS_CODE.md` | COMPLETE | Raw Mermaid & SQL diagram definitions for 1-click import |
| **ECOMMERCE_TESTING_AND_VIVA_GUIDE.md** | Markdown | `02_Ecommerce/ECOMMERCE_TESTING_AND_VIVA_GUIDE.md` | COMPLETE | Detailed viva presentation and oral defense walkthrough |
| **OpenAPI Contract** | YAML | `02_Ecommerce/openapi.yaml` | COMPLETE | OpenAPI 3.0 schema generated via drf-spectacular |
| **Database Schema** | SQL | `02_Ecommerce/schema.sql` | COMPLETE | DDL tables, foreign keys, and check constraints |
| **Environment Config** | Text | `02_Ecommerce/.env.example` | COMPLETE | Safe, uncommitted environment configuration template |

---

## 3. Rubric Self-Assessment (Project 02)

| Evaluation Rubric Dimension | Weight | Self-Score | Engineering Justification |
| :--- | :--- | :--- | :--- |
| **1. Problem Understanding & Requirements** | 20% | 20/20 | Complete implementation of e-commerce domain: stock check constraints, atomic checkout, frozen unit prices, order state machine, product detail modal. |
| **2. Architecture & System Design** | 25% | 25/25 | Pessimistic locking via `select_for_update()` with deterministic key ordering. Clean separation between DRF API and Next.js UI. Genuine Lucidchart diagrams linked. |
| **3. Implementation & Code Quality** | 25% | 25/25 | Django 5.2 best practices, PostgreSQL ACID transactions, Next.js 14 App Router, TypeScript interfaces, Tailwind CSS, and debounced search. |
| **4. Testing, Edge Cases & Verification** | 20% | 20/20 | 15 automated pytest tests with 100% pass rate. Real concurrency race condition test and SQL check violation test passing. |
| **5. Engineering Communication & Explanation**| 10% | 10/10 | Genuine Lucidchart links, vector PDFs, multi-tab Excel models with real formulas, and exhaustive engineering trade-off documentation. |
| **Total Project 02 Score** | **100%** | **100/100** | **Ready for Gate 2 Acceptance and Production Evaluation.** |
