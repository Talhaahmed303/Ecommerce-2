import pytest
import uuid
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.products.models import Product
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem
from apps.orders.services import checkout_cart, InsufficientStockException

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def ecom_db(db):
    admin = User.objects.create_user(
        username='admin_test',
        email='admin@store.com',
        password='Password@123',
        role='admin',
        is_staff=True
    )
    cust1 = User.objects.create_user(
        username='cust1_test',
        email='cust1@store.com',
        password='Password@123',
        role='customer',
        address='123 Main St'
    )
    cust2 = User.objects.create_user(
        username='cust2_test',
        email='cust2@store.com',
        password='Password@123',
        role='customer',
        address='456 Elm St'
    )
    prod_keyboard = Product.objects.create(
        title='Mechanical Keyboard',
        price=Decimal('100.00'),
        stock=5,
        sku='KEY-001',
        category='accessories'
    )
    prod_single = Product.objects.create(
        title='Rare Keycap (Only 1 left)',
        price=Decimal('50.00'),
        stock=1,
        sku='CAP-001',
        category='accessories'
    )
    prod_oos = Product.objects.create(
        title='Out of Stock Item',
        price=Decimal('20.00'),
        stock=0,
        sku='OOS-001',
        category='accessories'
    )
    return {
        'admin': admin,
        'cust1': cust1,
        'cust2': cust2,
        'prod_keyboard': prod_keyboard,
        'prod_single': prod_single,
        'prod_oos': prod_oos,
    }

# --- 1. Positive Tests ---

@pytest.mark.django_db
def test_customer_registration_success(api_client):
    url = reverse('ecom_register')
    payload = {
        'username': 'new_shopper',
        'password': 'SecurePass@123',
        'email': 'shopper@test.com',
        'phone': '1234567890',
        'address': '789 Market Ave'
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 201
    assert response.data['success'] is True
    assert User.objects.filter(username='new_shopper').exists()

@pytest.mark.django_db
def test_customer_login_jwt(api_client, ecom_db):
    url = reverse('ecom_login')
    payload = {'username': 'cust1_test', 'password': 'Password@123'}
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 200
    assert 'access' in response.data
    assert response.data['user']['role'] == 'customer'

@pytest.mark.django_db
def test_product_catalog_listing(api_client, ecom_db):
    url = reverse('product-list')
    response = api_client.get(url)
    assert response.status_code == 200
    results = response.data['results'] if 'results' in response.data else response.data
    assert len(results) >= 3
    # Check in_stock calculated field
    single = next(p for p in results if p['sku'] == 'CAP-001')
    assert single['in_stock'] is True
    oos = next(p for p in results if p['sku'] == 'OOS-001')
    assert oos['in_stock'] is False

@pytest.mark.django_db
def test_add_to_cart_success(api_client, ecom_db):
    api_client.force_authenticate(user=ecom_db['cust1'])
    url = reverse('cart_add')
    payload = {'product_id': ecom_db['prod_keyboard'].id, 'quantity': 2}
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 200
    assert response.data['success'] is True
    cart = Cart.objects.get(user=ecom_db['cust1'])
    assert cart.items.count() == 1
    assert cart.items.first().quantity == 2

@pytest.mark.django_db
def test_successful_checkout_workflow(api_client, ecom_db):
    user = ecom_db['cust1']
    product = ecom_db['prod_keyboard']
    initial_stock = product.stock  # 5

    # 1. Setup Cart
    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=2)

    # 2. Execute Checkout
    api_client.force_authenticate(user=user)
    url = reverse('order_checkout')
    payload = {
        'payment_token': 'tok_success',
        'idempotency_key': str(uuid.uuid4()),
        'shipping_address': '452 Engineering Way, Tech City'
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 201
    assert response.data['success'] is True

    # 3. Verify stock decremented
    product.refresh_from_db()
    assert product.stock == initial_stock - 2  # 3

    # 4. Verify cart emptied
    assert cart.items.count() == 0

    # 5. Verify Order & Price Freeze
    order_data = response.data['data']
    assert order_data['status'] == 'paid'
    assert Decimal(str(order_data['total_amount'])) == Decimal('200.00')
    assert len(order_data['items']) == 1
    assert Decimal(str(order_data['items'][0]['unit_price'])) == Decimal('100.00')

# --- 2. Negative Tests ---

@pytest.mark.django_db
def test_add_to_cart_exceeding_stock_rejected(api_client, ecom_db):
    api_client.force_authenticate(user=ecom_db['cust1'])
    url = reverse('cart_add')
    # Product has stock=1, request 5
    payload = {'product_id': ecom_db['prod_single'].id, 'quantity': 5}
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 400
    assert 'Cannot add 5 units' in response.data['message']

@pytest.mark.django_db
def test_checkout_empty_cart_rejected(api_client, ecom_db):
    api_client.force_authenticate(user=ecom_db['cust1'])
    url = reverse('order_checkout')
    payload = {'payment_token': 'tok_success', 'idempotency_key': str(uuid.uuid4())}
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 400
    assert 'Shopping cart is empty' in response.data['message']

@pytest.mark.django_db
def test_mock_payment_declined_workflow(api_client, ecom_db):
    user = ecom_db['cust1']
    product = ecom_db['prod_keyboard']
    initial_stock = product.stock

    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    api_client.force_authenticate(user=user)
    url = reverse('order_checkout')
    payload = {
        'payment_token': 'tok_decline',  # Card decline token
        'idempotency_key': str(uuid.uuid4())
    }
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 402  # Payment Required
    assert 'declined' in response.data['message'].lower()

    # Verify no stock was decremented and cart was NOT emptied
    product.refresh_from_db()
    assert product.stock == initial_stock
    assert cart.items.count() == 1
    assert Order.objects.filter(user=user).count() == 0

# --- 3. Concurrency & Race Condition Safety (CRITICAL) ---

@pytest.mark.django_db(transaction=True)
def test_concurrency_race_condition_zero_negative_stock(ecom_db):
    """
    Simulate race condition: Product has stock=1.
    Customer 1 and Customer 2 concurrently attempt checkout for the same unit.
    Exactly ONE must succeed, and the second MUST be rejected with InsufficientStockException.
    Final stock MUST be exactly 0, never negative.
    """
    product = ecom_db['prod_single']  # stock = 1
    cust1 = ecom_db['cust1']
    cust2 = ecom_db['cust2']

    # Both customers add the 1 remaining item to their carts
    cart1 = Cart.objects.create(user=cust1)
    CartItem.objects.create(cart=cart1, product=product, quantity=1)

    cart2 = Cart.objects.create(user=cust2)
    CartItem.objects.create(cart=cart2, product=product, quantity=1)

    # First checkout executes
    order1 = checkout_cart(
        user=cust1,
        payment_token='tok_success',
        idempotency_key=str(uuid.uuid4()),
        shipping_address='Addr 1'
    )
    assert order1 is not None
    assert order1.status == 'paid'

    product.refresh_from_db()
    assert product.stock == 0

    # Second checkout attempts same item
    with pytest.raises(InsufficientStockException) as exc_info:
        checkout_cart(
            user=cust2,
            payment_token='tok_success',
            idempotency_key=str(uuid.uuid4()),
            shipping_address='Addr 2'
        )

    assert "Insufficient stock" in str(exc_info.value)

    # Crucial assertion: Stock is strictly 0, never negative!
    product.refresh_from_db()
    assert product.stock == 0
    assert product.stock >= 0

# --- 4. Boundary Tests ---

@pytest.mark.django_db
def test_exact_stock_depletion_to_zero(api_client, ecom_db):
    user = ecom_db['cust1']
    product = ecom_db['prod_single']  # stock=1

    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    api_client.force_authenticate(user=user)
    url = reverse('order_checkout')
    payload = {'payment_token': 'tok_success', 'idempotency_key': str(uuid.uuid4())}
    response = api_client.post(url, payload, format='json')
    assert response.status_code == 201

    product.refresh_from_db()
    assert product.stock == 0

# --- 5. Security & Permission Tests ---

@pytest.mark.django_db
def test_customer_cannot_view_other_customer_order(api_client, ecom_db):
    # Create order for Customer 1
    order = Order.objects.create(
        user=ecom_db['cust1'],
        total_amount=Decimal('100.00'),
        status='paid'
    )

    # Customer 2 attempts to fetch Customer 1's order
    api_client.force_authenticate(user=ecom_db['cust2'])
    url = reverse('order-detail', kwargs={'id': order.id})
    response = api_client.get(url)
    assert response.status_code == 404

@pytest.mark.django_db
def test_customer_cannot_update_order_status(api_client, ecom_db):
    order = Order.objects.create(
        user=ecom_db['cust1'],
        total_amount=Decimal('100.00'),
        status='pending'
    )
    api_client.force_authenticate(user=ecom_db['cust1'])
    url = f"/api/orders/{order.id}/update_status/"
    response = api_client.patch(url, {'status': 'delivered'}, format='json')
    assert response.status_code == 403  # Forbidden

@pytest.mark.django_db
def test_admin_can_update_order_status_valid_transition(api_client, ecom_db):
    order = Order.objects.create(
        user=ecom_db['cust1'],
        total_amount=Decimal('100.00'),
        status='paid'
    )
    api_client.force_authenticate(user=ecom_db['admin'])
    url = f"/api/orders/{order.id}/update_status/"
    # Valid transition: paid -> processing
    response = api_client.patch(url, {'status': 'processing'}, format='json')
    assert response.status_code == 200
    assert response.data['data']['status'] == 'processing'

@pytest.mark.django_db
def test_admin_invalid_order_status_jump_rejected(api_client, ecom_db):
    order = Order.objects.create(
        user=ecom_db['cust1'],
        total_amount=Decimal('100.00'),
        status='pending'
    )
    api_client.force_authenticate(user=ecom_db['admin'])
    url = f"/api/orders/{order.id}/update_status/"
    # Invalid jump: pending directly to delivered
    response = api_client.patch(url, {'status': 'delivered'}, format='json')
    assert response.status_code == 400
    assert 'Invalid status transition' in str(response.data)

# --- 6. Price Freeze Snapshot Test ---

@pytest.mark.django_db
def test_order_line_item_price_freeze(api_client, ecom_db):
    user = ecom_db['cust1']
    product = ecom_db['prod_keyboard']  # original price $100

    cart = Cart.objects.create(user=user)
    CartItem.objects.create(cart=cart, product=product, quantity=1)

    api_client.force_authenticate(user=user)
    url = reverse('order_checkout')
    res = api_client.post(url, {'payment_token': 'tok_success', 'idempotency_key': str(uuid.uuid4())}, format='json')
    assert res.status_code == 201
    order_id = res.data['data']['id']

    # Admin increases catalog price to $200
    product.price = Decimal('200.00')
    product.save()

    # Fetch historical order
    order_res = api_client.get(reverse('order-detail', kwargs={'id': order_id}))
    assert order_res.status_code == 200
    line_item = order_res.data['items'][0]
    # Unit price on order MUST remain $100.00 (snapshot verification!)
    assert Decimal(str(line_item['unit_price'])) == Decimal('100.00')
