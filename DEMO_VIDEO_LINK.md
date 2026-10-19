# 02_ECOMMERCE — 3–5 MINUTE DEMO VIDEO WALKTHROUGH

**Candidate:** Talha Ahmed  
**Project:** High-Integrity E-Commerce Store (NovaMart)  

### 🎥 Google Drive Demo Video:
[▶️ Click to Watch 02_Ecommerce Demo Video](https://drive.google.com/file/d/188jZ0az2y0jtlESSNeMaqs3rUR2J5Tqg/view?usp=sharing)

**Raw URL:**  
`https://drive.google.com/file/d/188jZ0az2y0jtlESSNeMaqs3rUR2J5Tqg/view?usp=sharing`

---

### What is covered in the video:
1. Local Bare-Metal Setup (Backend Django Port 8002, Frontend Next.js Port 3002, PostgreSQL 18).
2. Product catalog, real-time warehouse stock badges, and interactive Quick View modal.
3. Cart management with live stock guards and subtotal computations.
4. Concurrency-safe atomic checkout (`select_for_update()`) and SQL `CHECK (stock >= 0)`.
5. Mock payment gateway token simulation (`tok_success` vs `tok_decline`) with idempotency.
6. Order isolation across customer accounts (Alice, Talha, Sara) and admin fulfillment FSM.
7. Execution proof of all 15 automated tests passing with 100% success rate.
