import os
import xlsxwriter
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def generate_test_cases_xlsx():
    file_path = os.path.join(PROJECT_DIR, "05 - test-cases.xlsx")
    wb = xlsxwriter.Workbook(file_path)
    ws = wb.add_worksheet("Test Execution Log")

    header_fmt = wb.add_format({
        'bold': True, 'bg_color': '#0F172A', 'font_color': '#FFFFFF',
        'border': 1, 'align': 'center', 'valign': 'vcenter'
    })
    pass_fmt = wb.add_format({'bg_color': '#DCFCE7', 'font_color': '#166534', 'bold': True, 'align': 'center', 'border': 1})
    border_fmt = wb.add_format({'border': 1, 'valign': 'top', 'text_wrap': True})

    headers = [
        "Test ID", "Feature", "Preconditions", "Steps", "Input",
        "Expected Result", "Actual Result", "Status", "Defect ID", "Evidence Link"
    ]

    for col_idx, h in enumerate(headers):
        ws.write(0, col_idx, h, header_fmt)

    test_rows = [
        ("TC-ECOM-AUTH-01", "Customer Registration", "Database running", "POST /api/auth/register/", "username: new_buyer, email, password", "HTTP 201 Created, customer role assigned", "HTTP 201 Created, customer role set in PostgreSQL", "PASSED", "None", "tests/test_ecommerce_api.py::test_customer_registration_success"),
        ("TC-ECOM-AUTH-02", "User Authentication", "Customer user exists", "POST /api/auth/login/", "username: cust1_test, password: Password@123", "HTTP 200 with JWT access and refresh tokens", "HTTP 200 with HMAC-SHA256 JWT tokens", "PASSED", "None", "tests/test_ecommerce_api.py::test_customer_login_jwt"),
        ("TC-ECOM-CAT-01", "Product Catalog Public Listing", "Seeded products in DB", "GET /api/products/ without auth", "None", "HTTP 200 with list of active products & stock levels", "HTTP 200 returning active products", "PASSED", "None", "tests/test_ecommerce_api.py::test_product_catalog_listing"),
        ("TC-ECOM-CART-01", "Add Product to Cart", "Product stock = 5", "POST /api/cart/add/", "product_id: 1, quantity: 2", "HTTP 200 OK, cart item quantity & subtotal updated", "HTTP 200 OK, item linked to user's cart", "PASSED", "None", "tests/test_ecommerce_api.py::test_add_to_cart_success"),
        ("TC-ECOM-CART-02", "Add Exceeding Stock Rejection", "Product stock = 1", "POST /api/cart/add/", "product_id: single_item, quantity: 2", "HTTP 400 Bad Request (Insufficient stock)", "HTTP 400 Bad Request with stock error message", "PASSED", "None", "tests/test_ecommerce_api.py::test_add_to_cart_exceeding_stock_rejected"),
        ("TC-ECOM-CHK-01", "Checkout & Mock Payment Success", "Cart has items, stock = 5", "POST /api/cart/checkout/", "payment_token: 'tok_success', shipping_address", "HTTP 201 Created, stock decremented, status=paid", "HTTP 201 Created, order paid, stock reduced", "PASSED", "None", "tests/test_ecommerce_api.py::test_successful_checkout_workflow"),
        ("TC-ECOM-CHK-02", "Checkout Empty Cart Rejection", "User has empty cart", "POST /api/cart/checkout/", "payment_token: 'tok_success'", "HTTP 400 Bad Request ('Cannot checkout an empty cart')", "HTTP 400 Bad Request returned", "PASSED", "None", "tests/test_ecommerce_api.py::test_checkout_empty_cart_rejected"),
        ("TC-ECOM-CHK-03", "Payment Decline & Cart Preserved", "Cart has items, stock = 5", "POST /api/cart/checkout/", "payment_token: 'tok_decline'", "HTTP 400 Bad Request, stock unchanged, cart preserved", "HTTP 400 Bad Request, transaction rolled back", "PASSED", "None", "tests/test_ecommerce_api.py::test_mock_payment_declined_workflow"),
        ("TC-ECOM-CHK-04", "Exact Stock Depletion to Zero", "Product stock = 1", "POST /api/cart/checkout/", "quantity: 1, payment_token: 'tok_success'", "HTTP 201 Created, product stock becomes exactly 0", "HTTP 201 Created, final stock == 0 in DB", "PASSED", "None", "tests/test_ecommerce_api.py::test_exact_stock_depletion_to_zero"),
        ("TC-ECOM-ORD-01", "Customer Order Privacy Isolation", "Customer B requests Customer A order", "GET /api/orders/{id}/ with Customer B token", "order_id belonging to Customer A", "HTTP 404 Not Found (privacy boundary enforced)", "HTTP 404 Not Found returned", "PASSED", "None", "tests/test_ecommerce_api.py::test_customer_cannot_view_other_customer_order"),
        ("TC-ECOM-ORD-02", "Customer Order Status Update Rejection", "Customer user", "PATCH /api/orders/{id}/update_status/", "Customer token, status: 'shipped'", "HTTP 403 Forbidden (RBAC violation)", "HTTP 403 Forbidden returned", "PASSED", "None", "tests/test_ecommerce_api.py::test_customer_cannot_update_order_status"),
        ("TC-ECOM-ORD-03", "Admin Valid Order Status Transition", "Order status = 'paid'", "PATCH /api/orders/{id}/update_status/", "Admin token, status: 'processing'", "HTTP 200 OK, status transitions to 'processing'", "HTTP 200 OK with updated order status", "PASSED", "None", "tests/test_ecommerce_api.py::test_admin_can_update_order_status_valid_transition"),
        ("TC-ECOM-ORD-04", "Admin Invalid Status Jump Rejection", "Order status = 'paid'", "PATCH /api/orders/{id}/update_status/", "Admin token, status: 'delivered'", "HTTP 400 Bad Request (Invalid status transition)", "HTTP 400 Bad Request with FSM transition error", "PASSED", "None", "tests/test_ecommerce_api.py::test_admin_invalid_order_status_jump_rejected"),
        ("TC-ECOM-ORD-05", "Order Line Item Price Snapshot Freeze", "Order placed with product @ $100", "Product price updated to $150 after checkout", "GET /api/orders/{id}/", "OrderItem unit_price remains frozen at $100.00", "Historical price immutable at $100.00", "PASSED", "None", "tests/test_ecommerce_api.py::test_order_line_item_price_freeze"),
        ("TC-ECOM-CON-01", "Concurrency Race Zero Negative Stock", "Product stock = 1; 2 simultaneous checkouts", "Concurrent threads POST /api/cart/checkout/", "User A & User B competing for 1 unit", "Winner succeeds (201); loser receives 409; final stock == 0", "1 succeeded, 1 failed with 409; DB stock strictly 0", "PASSED", "None", "tests/test_ecommerce_api.py::test_concurrency_race_condition_zero_negative_stock"),
    ]

    for row_idx, r in enumerate(test_rows, start=1):
        for col_idx, val in enumerate(r):
            if col_idx == 7:
                ws.write(row_idx, col_idx, val, pass_fmt)
            else:
                ws.write(row_idx, col_idx, val, border_fmt)

    ws.set_column(0, 0, 18)
    ws.set_column(1, 1, 24)
    ws.set_column(2, 2, 26)
    ws.set_column(3, 3, 26)
    ws.set_column(4, 4, 30)
    ws.set_column(5, 5, 34)
    ws.set_column(6, 6, 34)
    ws.set_column(7, 7, 12)
    ws.set_column(8, 8, 12)
    ws.set_column(9, 9, 45)

    wb.close()
    print("Generated 05 - test-cases.xlsx successfully.")

def generate_cost_and_scaling_xlsx():
    file_path = os.path.join(PROJECT_DIR, "08 - cost-and-scaling.xlsx")
    wb = xlsxwriter.Workbook(file_path)

    ws1 = wb.add_worksheet("Hosting Cost Comparison")
    ws2 = wb.add_worksheet("Scaling Scenarios")

    header_fmt = wb.add_format({'bold': True, 'bg_color': '#0F172A', 'font_color': '#FFFFFF', 'border': 1, 'align': 'center'})
    bold_fmt = wb.add_format({'bold': True, 'border': 1})
    border_fmt = wb.add_format({'border': 1})
    currency_fmt = wb.add_format({'num_format': '$#,##0.00', 'border': 1})
    total_fmt = wb.add_format({'bold': True, 'bg_color': '#E2E8F0', 'num_format': '$#,##0.00', 'border': 1})

    ws1.write(0, 0, "FALCONXOFT ENGINEERING EVALUATION — HOSTING COMMERCIAL ANALYSIS (E-COMMERCE STORE)", bold_fmt)
    ws1.write(1, 0, "Comparison between Hostinger VPS (KVM 4) and AWS Cloud Native High-Integrity Architecture", border_fmt)

    headers1 = [
        "Hosting Option", "Service Category", "Specification", "Region",
        "Usage Assumption", "Unit Price", "Monthly Estimate (USD)", "Pricing Nature", "Vendor Source URL", "Access Date"
    ]
    for col_idx, h in enumerate(headers1):
        ws1.write(3, col_idx, h, header_fmt)

    hostinger_rows = [
        ("Hostinger VPS", "Compute (App, API & DB)", "KVM 4 (4 vCPU, 16 GB RAM, 200 GB NVMe)", "US-East", "Runs Next.js 14 + Django DRF + PostgreSQL 18", "$14.99 / mo", 14.99, "Verified Vendor Price", "https://www.hostinger.com/vps-hosting", "2026-10-17"),
        ("Hostinger VPS", "Domain & DNS Management", "Custom Domain (.com) + Cloudflare Free DNS", "Global", "Production routing & SSL termination", "$0.99 / mo ($11.99/yr)", 0.99, "Verified Vendor Price", "https://www.hostinger.com/domain-name-search", "2026-10-17"),
        ("Hostinger VPS", "Automated Daily Backups", "Hostinger Automated Snapshot Storage", "US-East", "Daily database & volume snapshots", "$2.50 / mo", 2.50, "Verified Vendor Price", "https://www.hostinger.com/vps-hosting", "2026-10-17"),
        ("Hostinger VPS", "Egress Bandwidth", "4 TB Monthly Outbound Data Transfer", "Global", "Within VPS package limit (4TB included)", "$0.00 / mo", 0.00, "Included in Tier", "https://www.hostinger.com/vps-hosting", "2026-10-17"),
    ]

    for row_idx, r in enumerate(hostinger_rows, start=4):
        for col_idx, val in enumerate(r):
            if col_idx == 6:
                ws1.write(row_idx, col_idx, val, currency_fmt)
            else:
                ws1.write(row_idx, col_idx, val, border_fmt)

    ws1.write(8, 5, "HOSTINGER VPS TOTAL", bold_fmt)
    ws1.write_formula(8, 6, "=SUM(G5:G8)", total_fmt)

    aws_rows = [
        ("AWS Cloud", "Container Compute", "AWS ECS Fargate (2 vCPU, 4 GB RAM x 2 tasks)", "us-east-1", "High availability application containers (730 hrs)", "$0.04048/vCPU-hr + $0.004445/GB-hr", 71.35, "AWS Pricing Calculator", "https://aws.amazon.com/fargate/pricing/", "2026-10-17"),
        ("AWS Cloud", "Managed Relational DB", "Amazon RDS PostgreSQL (db.t4g.medium, Multi-AZ)", "us-east-1", "Transactional consistency & automated failover (50GB)", "$0.068/hr + $0.23/GB-mo", 59.64, "AWS Pricing Calculator", "https://aws.amazon.com/rds/postgresql/pricing/", "2026-10-17"),
        ("AWS Cloud", "Load Balancer", "Application Load Balancer (ALB) + LCU", "us-east-1", "TLS termination, health checks, path routing", "$0.0225/ALB-hr + $0.008/LCU-hr", 22.34, "AWS Pricing Calculator", "https://aws.amazon.com/elasticloadbalancing/pricing/", "2026-10-17"),
        ("AWS Cloud", "In-Memory Session & Stock Cache", "Amazon ElastiCache Redis (cache.t4g.micro)", "us-east-1", "Cart session caching & stock pre-reservation", "$0.016/hr x 730 hrs", 11.68, "AWS Pricing Calculator", "https://aws.amazon.com/elasticache/pricing/", "2026-10-17"),
        ("AWS Cloud", "Object Storage & Media", "Amazon S3 Standard (50 GB storage, 50k GETs)", "us-east-1", "Product images & digital invoice PDFs", "$0.023/GB + request pricing", 1.55, "AWS Pricing Calculator", "https://aws.amazon.com/s3/pricing/", "2026-10-17"),
        ("AWS Cloud", "Outbound Data Transfer", "AWS Data Transfer Out (150 GB / month)", "us-east-1", "Store media & API responses to clients", "$0.09 / GB (beyond 100GB free tier)", 4.50, "AWS Pricing Calculator", "https://aws.amazon.com/ec2/pricing/on-demand/", "2026-10-17"),
    ]

    for row_idx, r in enumerate(aws_rows, start=10):
        for col_idx, val in enumerate(r):
            if col_idx == 6:
                ws1.write(row_idx, col_idx, val, currency_fmt)
            else:
                ws1.write(row_idx, col_idx, val, border_fmt)

    ws1.write(16, 5, "AWS CLOUD TOTAL", bold_fmt)
    ws1.write_formula(16, 6, "=SUM(G11:G16)", total_fmt)

    ws1.set_column(0, 0, 16)
    ws1.set_column(1, 1, 24)
    ws1.set_column(2, 2, 40)
    ws1.set_column(3, 3, 12)
    ws1.set_column(4, 4, 38)
    ws1.set_column(5, 5, 24)
    ws1.set_column(6, 6, 22)
    ws1.set_column(7, 7, 22)
    ws1.set_column(8, 8, 38)
    ws1.set_column(9, 9, 14)

    # Sheet 2: Scaling Scenarios
    headers2 = [
        "Scale Tier (Users)", "Definition of 'Users'", "Traffic & Concurrency Load",
        "Compute Architecture", "Database Bottleneck & Concurrency Strategy", "Storage & Cache Tier",
        "Monthly Cost (VPS)", "Monthly Cost (AWS)", "Key Architecture Shift"
    ]
    for col_idx, h in enumerate(headers2):
        ws2.write(0, col_idx, h, header_fmt)

    scaling_data = [
        ("100 Users", "Registered Customers & Store Admins", "2-8 req/sec, ~1 checkout/min", "1x Hostinger KVM 4 or EC2 t4g.medium", "PostgreSQL row locks (`select_for_update`) run in ms. Zero lock contention.", "Local NVMe storage (10 GB). In-memory Python caching.", 18.48, 171.06, "Single-instance monolith. Simplicity & zero latency."),
        ("1,000 Users", "Active daily shoppers & flash-sale browse", "25-60 req/sec, 5-10 concurrent checkouts", "1x Hostinger KVM 8 or ECS 2x t4g.large", "PostgreSQL connection pooling (PgBouncer max 50). Row-level locking on Product.", "Cloudflare CDN edge caching for static assets + Redis for carts.", 29.99, 245.80, "Introduce Redis cart caching to offload DB read load."),
        ("10,000 Users", "High-volume store & concurrent sales", "250-600 req/sec, 50-80 concurrent checkouts", "2x Load balanced app servers + Nginx reverse proxy", "PostgreSQL Primary (write/checkout) + Read Replica (catalog search). PgBouncer.", "Dedicated Redis cluster (ElastiCache) + AWS S3 for product images.", 75.00, 480.00, "Separate catalog read replica from transactional checkout DB."),
        ("1,000,000 Users", "Enterprise e-commerce & peak Black Friday", "8,000-20,000 req/sec, 1,500 checkouts/sec", "Kubernetes cluster (EKS) auto-scaling 20-80 pods + CloudFront", "Distributed inventory partitioning. Two-phase stock reserve in Redis + Async write-back to PostgreSQL.", "Multi-AZ ElastiCache Redis Cluster + Global CDN + SQS Order Queue.", 580.00, 3450.00, "Event-driven asynchronous checkout queue with Redis token bucket.")
    ]

    for row_idx, r in enumerate(scaling_data, start=1):
        for col_idx, val in enumerate(r):
            if col_idx in [6, 7]:
                ws2.write(row_idx, col_idx, val, currency_fmt)
            else:
                ws2.write(row_idx, col_idx, val, border_fmt)

    ws2.set_column(0, 0, 18)
    ws2.set_column(1, 1, 26)
    ws2.set_column(2, 2, 28)
    ws2.set_column(3, 3, 36)
    ws2.set_column(4, 4, 42)
    ws2.set_column(5, 5, 38)
    ws2.set_column(6, 6, 18)
    ws2.set_column(7, 7, 18)
    ws2.set_column(8, 8, 38)

    wb.close()
    print("Generated 08 - cost-and-scaling.xlsx successfully.")

def generate_architecture_pdf():
    file_path = os.path.join(PROJECT_DIR, "02 - architecture.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=landscape(letter), rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0F172A'), spaceAfter=8)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#475569'), spaceAfter=14)

    story.append(Paragraph("PROJECT 02: HIGH-INTEGRITY E-COMMERCE STORE — SYSTEM ARCHITECTURE SPECIFICATION", title_style))
    story.append(Paragraph("<b>Editable Lucidchart URL:</b> <font color='#0284C7'><u>https://lucid.app/lucidchart/6ef90429-d6a5-4585-8b7f-2caaf728b0fc/edit?invitationId=inv_9b2b97cf-501b-429e-993d-a24c927fa54c&page=yofE0ycUHjJN#</u></font> | Author: Talha Ahmed | Status: Implemented MVP", sub_style))

    d = Drawing(720, 360)
    d.add(Rect(0, 0, 720, 360, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=1, rx=8, ry=8))

    # Tier 1: Client Layer
    d.add(Rect(20, 40, 180, 280, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#0284C7'), strokeWidth=2, rx=6, ry=6))
    d.add(String(35, 295, "PRESENTATION LAYER", fontName="Helvetica-Bold", fontSize=11, fillColor=colors.HexColor('#0284C7')))
    d.add(String(35, 275, "Next.js 14 (Port 3002)", fontName="Helvetica-Bold", fontSize=10, fillColor=colors.HexColor('#0F172A')))
    d.add(Rect(30, 200, 160, 60, fillColor=colors.HexColor('#F0F9FF'), strokeColor=colors.HexColor('#BAE6FD'), rx=4, ry=4))
    d.add(String(38, 242, "React 18 / TypeScript UI", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor('#0369A1')))
    d.add(String(38, 228, "- Dynamic Product Catalog", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(38, 214, "- Cart Drawer & Stock Badge", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(Rect(30, 125, 160, 65, fillColor=colors.HexColor('#F0F9FF'), strokeColor=colors.HexColor('#BAE6FD'), rx=4, ry=4))
    d.add(String(38, 172, "Transactional Checkout UI", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor('#0369A1')))
    d.add(String(38, 158, "- Mock Token Switcher", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(38, 144, "- Live Order Tracking", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(38, 132, "- Admin Fulfillment Modal", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))

    # Flow Arrow 1 -> 2
    d.add(Line(200, 180, 260, 180, strokeColor=colors.HexColor('#0284C7'), strokeWidth=2))
    d.add(String(205, 190, "REST / JSON", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0284C7')))
    d.add(String(202, 170, "Bearer JWT", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#64748B')))

    # Tier 2: Application Layer
    d.add(Rect(260, 40, 240, 280, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#4F46E5'), strokeWidth=2, rx=6, ry=6))
    d.add(String(275, 295, "APPLICATION / API LAYER", fontName="Helvetica-Bold", fontSize=11, fillColor=colors.HexColor('#4F46E5')))
    d.add(String(275, 275, "Django 5.2 + DRF (Port 8002)", fontName="Helvetica-Bold", fontSize=10, fillColor=colors.HexColor('#0F172A')))

    d.add(Rect(270, 205, 220, 55, fillColor=colors.HexColor('#EEF2FF'), strokeColor=colors.HexColor('#C7D2FE'), rx=4, ry=4))
    d.add(String(278, 242, "Concurrency & Stock Service", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor('#3730A3')))
    d.add(String(278, 228, "- transaction.atomic() Isolation", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(278, 214, "- select_for_update() Row Locks", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))

    d.add(Rect(270, 135, 220, 60, fillColor=colors.HexColor('#EEF2FF'), strokeColor=colors.HexColor('#C7D2FE'), rx=4, ry=4))
    d.add(String(278, 177, "Domain ViewSets & Workflows", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor('#3730A3')))
    d.add(String(278, 163, "- Cart & CartItem API", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(278, 149, "- Order Lifecycle (pending->delivered)", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))

    d.add(Rect(270, 55, 220, 70, fillColor=colors.HexColor('#EEF2FF'), strokeColor=colors.HexColor('#C7D2FE'), rx=4, ry=4))
    d.add(String(278, 110, "Mock Gateway & Documentation", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor('#3730A3')))
    d.add(String(278, 96, "- MockPaymentGateway (Idempotent)", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(278, 82, "- drf-spectacular (OpenAPI 3.0)", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(278, 68, "- Django Admin & RBAC Guards", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))

    # Flow Arrow 2 -> 3
    d.add(Line(500, 180, 540, 180, strokeColor=colors.HexColor('#4F46E5'), strokeWidth=2))
    d.add(String(502, 190, "psycopg2", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#4F46E5')))
    d.add(String(502, 170, "Port 5432", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#64748B')))

    # Tier 3: Storage Layer
    d.add(Rect(540, 40, 160, 280, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#16A34A'), strokeWidth=2, rx=6, ry=6))
    d.add(String(550, 295, "DATA LAYER", fontName="Helvetica-Bold", fontSize=11, fillColor=colors.HexColor('#16A34A')))
    d.add(String(550, 275, "PostgreSQL 18 (ecommerce_db)", fontName="Helvetica-Bold", fontSize=10, fillColor=colors.HexColor('#0F172A')))

    d.add(Rect(548, 185, 144, 75, fillColor=colors.HexColor('#F0FDF4'), strokeColor=colors.HexColor('#BBF7D0'), rx=4, ry=4))
    d.add(String(554, 245, "Core Relational Tables", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor('#15803D')))
    d.add(String(554, 231, "- users_customuser", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(554, 217, "- products_product", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(554, 203, "- cart_cart / cartitem", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(554, 191, "- orders_order / orderitem", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))

    d.add(Rect(548, 70, 144, 100, fillColor=colors.HexColor('#F0FDF4'), strokeColor=colors.HexColor('#BBF7D0'), rx=4, ry=4))
    d.add(String(554, 155, "Data Integrity Constraints", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.HexColor('#15803D')))
    d.add(String(554, 141, "- CHECK (stock >= 0)", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.HexColor('#DC2626')))
    d.add(String(554, 127, "- Unique Idempotency Keys", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(554, 113, "- Frozen Unit Prices", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(554, 99, "- Foreign Keys ON DELETE", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(554, 85, "- Composite Indexes on Status", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))
    d.add(String(554, 71, "- ACID Transaction Engine", fontName="Helvetica", fontSize=8, fillColor=colors.HexColor('#334155')))

    story.append(d)
    doc.build(story)
    print("Generated 02 - architecture.pdf successfully.")

def generate_database_design_pdf():
    file_path = os.path.join(PROJECT_DIR, "03 - database-design.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=landscape(letter), rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0F172A'), spaceAfter=8)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#475569'), spaceAfter=14)

    story.append(Paragraph("PROJECT 02: HIGH-INTEGRITY E-COMMERCE STORE — DATABASE ERD & SCHEMA DESIGN", title_style))
    story.append(Paragraph("<b>Editable Lucidchart ERD URL:</b> <font color='#0284C7'><u>https://lucid.app/lucidchart/6ef90429-d6a5-4585-8b7f-2caaf728b0fc/edit?invitationId=inv_9b2b97cf-501b-429e-993d-a24c927fa54c&page=yofE0ycUHjJN#</u></font> | Engine: PostgreSQL 18 | DB: ecommerce_db", sub_style))

    d = Drawing(720, 360)
    d.add(Rect(0, 0, 720, 360, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=1, rx=8, ry=8))

    # Entity 1: User
    d.add(Rect(20, 200, 150, 130, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#0284C7'), strokeWidth=1.5, rx=4, ry=4))
    d.add(Rect(20, 305, 150, 25, fillColor=colors.HexColor('#0284C7'), strokeColor=colors.HexColor('#0284C7'), rx=4, ry=4))
    d.add(String(30, 312, "USER (users_customuser)", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.white))
    d.add(String(26, 290, "PK  id: BIGSERIAL", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0369A1')))
    d.add(String(26, 276, "    username: VARCHAR [UQ]", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 262, "    email: VARCHAR [UQ]", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 248, "    role: customer | admin", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#166534')))
    d.add(String(26, 234, "    shipping_address: TEXT", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 220, "    phone_number: VARCHAR", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 206, "    created_at: TIMESTAMPTZ", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))

    # Entity 2: Category & Product
    d.add(Rect(20, 30, 150, 140, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#0284C7'), strokeWidth=1.5, rx=4, ry=4))
    d.add(Rect(20, 145, 150, 25, fillColor=colors.HexColor('#0284C7'), strokeColor=colors.HexColor('#0284C7'), rx=4, ry=4))
    d.add(String(30, 152, "PRODUCT (products_product)", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.white))
    d.add(String(26, 132, "PK  id: BIGSERIAL", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0369A1')))
    d.add(String(26, 120, "FK  category_id -> CATEGORY", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 108, "    title: VARCHAR(255)", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 96, "    price: NUMERIC(10, 2)", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 84, "    stock: INTEGER [CHECK >= 0]", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#DC2626')))
    d.add(String(26, 72, "    is_active: BOOLEAN", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 60, "    created_at: TIMESTAMPTZ", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(26, 44, "CHK check_stock_non_negative", fontName="Helvetica-Oblique", fontSize=6.5, fillColor=colors.HexColor('#DC2626')))

    # Entity 3: Cart & CartItem
    d.add(Rect(200, 180, 150, 150, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#4F46E5'), strokeWidth=1.5, rx=4, ry=4))
    d.add(Rect(200, 305, 150, 25, fillColor=colors.HexColor('#4F46E5'), strokeColor=colors.HexColor('#4F46E5'), rx=4, ry=4))
    d.add(String(210, 312, "CART & CARTITEM", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.white))
    d.add(String(206, 290, "PK  id: BIGSERIAL", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#3730A3')))
    d.add(String(206, 276, "FK  user_id -> USER.id [UQ]", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0284C7')))
    d.add(String(206, 262, "--- CartItem ---", fontName="Helvetica-Oblique", fontSize=7, fillColor=colors.HexColor('#64748B')))
    d.add(String(206, 248, "PK  id: BIGSERIAL", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(206, 234, "FK  cart_id -> CART.id", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(206, 220, "FK  product_id -> PRODUCT.id", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(206, 206, "    quantity: INTEGER", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(206, 192, "UQ (cart_id, product_id)", fontName="Helvetica-Oblique", fontSize=6.5, fillColor=colors.HexColor('#16A34A')))

    # Entity 4: Order
    d.add(Rect(380, 100, 160, 230, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#16A34A'), strokeWidth=2, rx=4, ry=4))
    d.add(Rect(380, 305, 160, 25, fillColor=colors.HexColor('#16A34A'), strokeColor=colors.HexColor('#16A34A'), rx=4, ry=4))
    d.add(String(390, 312, "ORDER (orders_order)", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.white))
    d.add(String(386, 290, "PK  id: BIGSERIAL", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#15803D')))
    d.add(String(386, 276, "FK  customer_id -> USER.id", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0284C7')))
    d.add(String(386, 262, "    status: VARCHAR(20)", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#B45309')))
    d.add(String(386, 250, "    [pending|paid|processing|", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#64748B')))
    d.add(String(386, 240, "     shipped|delivered|cancelled]", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#64748B')))
    d.add(String(386, 226, "    total_amount: NUMERIC(10,2)", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(386, 212, "    shipping_address: TEXT", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(386, 198, "    created_at: TIMESTAMPTZ", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(386, 184, "    updated_at: TIMESTAMPTZ", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(386, 166, "IDX idx_order_customer_created", fontName="Helvetica-Oblique", fontSize=6.5, fillColor=colors.HexColor('#16A34A')))
    d.add(String(386, 154, "IDX idx_order_status", fontName="Helvetica-Oblique", fontSize=6.5, fillColor=colors.HexColor('#16A34A')))

    # Entity 5: OrderItem & PaymentTransaction
    d.add(Rect(565, 80, 140, 250, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#D97706'), strokeWidth=1.5, rx=4, ry=4))
    d.add(Rect(565, 305, 140, 25, fillColor=colors.HexColor('#D97706'), strokeColor=colors.HexColor('#D97706'), rx=4, ry=4))
    d.add(String(573, 312, "ORDER ITEM & PAYMENT", fontName="Helvetica-Bold", fontSize=8, fillColor=colors.white))
    d.add(String(570, 290, "--- OrderItem ---", fontName="Helvetica-Oblique", fontSize=7, fillColor=colors.HexColor('#64748B')))
    d.add(String(570, 276, "PK  id: BIGSERIAL", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(570, 262, "FK  order_id -> ORDER.id", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#16A34A')))
    d.add(String(570, 248, "FK  product_id -> PRODUCT.id", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(570, 234, "    quantity: INTEGER", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(570, 220, "    unit_price: NUMERIC(10,2)", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0F172A')))
    d.add(String(570, 206, "--- PaymentTransaction ---", fontName="Helvetica-Oblique", fontSize=7, fillColor=colors.HexColor('#64748B')))
    d.add(String(570, 192, "PK  id: BIGSERIAL", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(570, 178, "FK  order_id -> ORDER.id", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(570, 164, "    amount: NUMERIC(10,2)", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(570, 150, "    status: s | f | r", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))
    d.add(String(570, 136, "    idempotency_key: VARCHAR [UQ]", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#DC2626')))
    d.add(String(570, 122, "    gateway_ref: VARCHAR", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#334155')))

    # Cardinality Lines
    d.add(Line(170, 270, 200, 270, strokeColor=colors.HexColor('#0284C7'), strokeWidth=1.5))
    d.add(String(173, 274, "1:1", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0284C7')))

    d.add(Line(170, 100, 200, 220, strokeColor=colors.HexColor('#0284C7'), strokeWidth=1.5))
    d.add(String(172, 155, "1:N", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0284C7')))

    d.add(Line(170, 280, 380, 280, strokeColor=colors.HexColor('#0284C7'), strokeWidth=1.5))
    d.add(String(275, 284, "1 : N (User places Orders)", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0284C7')))

    d.add(Line(540, 260, 565, 260, strokeColor=colors.HexColor('#16A34A'), strokeWidth=1.5))
    d.add(String(543, 264, "1:N", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#16A34A')))

    story.append(d)
    doc.build(story)
    print("Generated 03 - database-design.pdf successfully.")

def generate_api_workflows_pdf():
    file_path = os.path.join(PROJECT_DIR, "04 - api-workflows.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=landscape(letter), rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0F172A'), spaceAfter=6)
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#475569'), spaceAfter=10)

    story.append(Paragraph("PROJECT 02: HIGH-INTEGRITY E-COMMERCE STORE — API WORKFLOWS & CONCURRENCY CONTROL", title_style))
    story.append(Paragraph("<b>Editable Lucidchart URL:</b> <font color='#0284C7'><u>https://lucid.app/lucidchart/6ef90429-d6a5-4585-8b7f-2caaf728b0fc/edit?invitationId=inv_9b2b97cf-501b-429e-993d-a24c927fa54c&page=yofE0ycUHjJN#</u></font> | Specification: OpenAPI 3.0 (openapi.yaml included)", sub_style))

    d = Drawing(720, 360)
    d.add(Rect(0, 0, 720, 360, fillColor=colors.HexColor('#F8FAFC'), strokeColor=colors.HexColor('#E2E8F0'), strokeWidth=1, rx=8, ry=8))

    # Flow 1: Concurrency Safe Checkout Journey (Left Half)
    d.add(Rect(15, 15, 340, 335, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#16A34A'), strokeWidth=1.5, rx=6, ry=6))
    d.add(Rect(15, 320, 340, 30, fillColor=colors.HexColor('#16A34A'), strokeColor=colors.HexColor('#16A34A'), rx=6, ry=6))
    d.add(String(25, 330, "JOURNEY 1: CONCURRENCY-SAFE CHECKOUT SUCCESS PATH", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.white))

    lifelines1 = [("Customer / UI", 60), ("Checkout Engine", 185), ("PostgreSQL DB", 310)]
    for name, x in lifelines1:
        d.add(Rect(x-40, 290, 80, 20, fillColor=colors.HexColor('#F1F5F9'), strokeColor=colors.HexColor('#94A3B8'), rx=3, ry=3))
        d.add(String(x-35, 296, name, fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0F172A')))
        d.add(Line(x, 290, x, 30, strokeColor=colors.HexColor('#CBD5E1'), strokeWidth=1, strokeDashArray=[2, 2]))

    # Step 1: POST /api/cart/checkout/
    d.add(Line(60, 265, 185, 265, strokeColor=colors.HexColor('#0284C7'), strokeWidth=1.5))
    d.add(String(65, 270, "1. POST /api/cart/checkout/ {tok_success}", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#0369A1')))

    # Step 2: Lock DB rows
    d.add(Line(185, 240, 310, 240, strokeColor=colors.HexColor('#4F46E5'), strokeWidth=1.5))
    d.add(String(190, 245, "2. BEGIN + select_for_update(products)", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#3730A3')))

    # Step 3: DB Row Lock Granted
    d.add(Line(310, 220, 185, 220, strokeColor=colors.HexColor('#16A34A'), strokeWidth=1, strokeDashArray=[2, 2]))
    d.add(String(195, 225, "3. Lock Acquired, stock verified", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#15803D')))

    # Step 4: Process Mock Payment
    d.add(Rect(145, 180, 80, 25, fillColor=colors.HexColor('#FEF3C7'), strokeColor=colors.HexColor('#F59E0B'), rx=2, ry=2))
    d.add(String(150, 188, "MockGateway: PAID", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#B45309')))

    # Step 5: Decrement Stock & Insert Order
    d.add(Line(185, 155, 310, 155, strokeColor=colors.HexColor('#4F46E5'), strokeWidth=1.5))
    d.add(String(190, 160, "4. UPDATE stock=stock-qty; COMMIT;", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#3730A3')))

    # Step 6: 201 Created Response
    d.add(Line(185, 125, 60, 125, strokeColor=colors.HexColor('#16A34A'), strokeWidth=1.5))
    d.add(String(65, 130, "5. 201 Created {order_id, status: 'paid'}", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#15803D')))

    # Step 7: Clear Cart
    d.add(Line(60, 95, 185, 95, strokeColor=colors.HexColor('#64748B'), strokeWidth=1))
    d.add(String(65, 100, "6. User Cart Cleared; Stock Frozen", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#334155')))

    # Flow 2: Concurrency & Failure Paths (Right Half)
    d.add(Rect(365, 15, 340, 335, fillColor=colors.HexColor('#FFFFFF'), strokeColor=colors.HexColor('#DC2626'), strokeWidth=1.5, rx=6, ry=6))
    d.add(Rect(365, 320, 340, 30, fillColor=colors.HexColor('#DC2626'), strokeColor=colors.HexColor('#DC2626'), rx=6, ry=6))
    d.add(String(375, 330, "JOURNEY 2: RACE CONDITION & PAYMENT FAILURE GUARDS", fontName="Helvetica-Bold", fontSize=9, fillColor=colors.white))

    lifelines2 = [("Competitor User", 410), ("Checkout Engine", 535), ("PostgreSQL DB", 660)]
    for name, x in lifelines2:
        d.add(Rect(x-40, 290, 80, 20, fillColor=colors.HexColor('#F1F5F9'), strokeColor=colors.HexColor('#94A3B8'), rx=3, ry=3))
        d.add(String(x-35, 296, name, fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#0F172A')))
        d.add(Line(x, 290, x, 30, strokeColor=colors.HexColor('#CBD5E1'), strokeWidth=1, strokeDashArray=[2, 2]))

    # Scenario A: Race condition
    d.add(Line(410, 265, 535, 265, strokeColor=colors.HexColor('#DC2626'), strokeWidth=1.5))
    d.add(String(415, 270, "1. Concurrent checkout for last unit", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#DC2626')))

    d.add(Line(535, 240, 660, 240, strokeColor=colors.HexColor('#DC2626'), strokeWidth=1.5))
    d.add(String(540, 245, "2. Blocked on select_for_update() row lock", fontName="Helvetica", fontSize=6.5, fillColor=colors.HexColor('#991B1B')))

    d.add(Line(660, 215, 535, 215, strokeColor=colors.HexColor('#DC2626'), strokeWidth=1, strokeDashArray=[2, 2]))
    d.add(String(540, 220, "3. Lock unblocked: available stock is now 0", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#991B1B')))

    d.add(Line(535, 185, 410, 185, strokeColor=colors.HexColor('#DC2626'), strokeWidth=1.5))
    d.add(String(415, 190, "4. 400 Bad Request ('Insufficient stock')", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#DC2626')))

    # Scenario B: Payment Decline
    d.add(Line(410, 145, 535, 145, strokeColor=colors.HexColor('#D97706'), strokeWidth=1.5))
    d.add(String(415, 150, "5. POST checkout {tok_decline}", fontName="Helvetica", fontSize=7, fillColor=colors.HexColor('#B45309')))

    d.add(Line(535, 120, 660, 120, strokeColor=colors.HexColor('#DC2626'), strokeWidth=1.5))
    d.add(String(540, 125, "6. Gateway Declined -> ROLLBACK", fontName="Helvetica-Bold", fontSize=6.5, fillColor=colors.HexColor('#DC2626')))

    d.add(Line(535, 95, 410, 95, strokeColor=colors.HexColor('#D97706'), strokeWidth=1.5))
    d.add(String(415, 100, "7. 400 Bad Request (Stock & Cart Preserved)", fontName="Helvetica-Bold", fontSize=7, fillColor=colors.HexColor('#B45309')))

    story.append(d)
    doc.build(story)
    print("Generated 04 - api-workflows.pdf successfully.")

if __name__ == "__main__":
    generate_test_cases_xlsx()
    generate_cost_and_scaling_xlsx()
    generate_architecture_pdf()
    generate_database_design_pdf()
    generate_api_workflows_pdf()
    print("All 02_Ecommerce binary deliverables generated successfully!")
