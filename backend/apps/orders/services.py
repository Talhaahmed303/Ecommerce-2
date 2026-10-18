from django.db import transaction
from apps.cart.models import Cart
from apps.products.models import Product
from apps.payments.services import MockPaymentGateway
from .models import Order, OrderItem

class InsufficientStockException(Exception):
    pass

class PaymentDeclinedException(Exception):
    def __init__(self, message, tx=None):
        super().__init__(message)
        self.tx = tx

class EmptyCartException(Exception):
    pass

def checkout_cart(user, payment_token, idempotency_key, shipping_address):
    """
    Executes an atomic, concurrency-safe checkout workflow.
    Guarantees:
    - Products are locked with select_for_update() in deterministic order to eliminate race conditions.
    - Stock can NEVER become negative under concurrent checkout attempts.
    - Mock payments represent success vs decline honestly.
    - Prices are frozen as immutable line items in OrderItem records.
    """
    with transaction.atomic():
        # 1. Fetch user's cart
        cart = Cart.objects.filter(user=user).first()
        if not cart or not cart.items.exists():
            raise EmptyCartException("Shopping cart is empty.")

        cart_items = list(cart.items.select_related('product').all())
        product_ids = sorted([item.product_id for item in cart_items])

        # 2. Acquire pessimistic row-level locks on products (PostgreSQL: SELECT ... FOR UPDATE)
        locked_products = {
            p.id: p 
            for p in Product.objects.select_for_update().filter(id__in=product_ids)
        }

        # 3. Check stock under lock
        for item in cart_items:
            product = locked_products.get(item.product_id)
            if not product or not product.is_active:
                raise InsufficientStockException(f"Product '{item.product.title}' is no longer active.")
            if product.stock < item.quantity:
                raise InsufficientStockException(
                    f"Insufficient stock for '{product.title}'. Requested {item.quantity}, but only {product.stock} available."
                )

        # 4. Calculate total amount
        total_amount = sum(item.product.price * item.quantity for item in cart_items)

        # 5. Process Payment via Mock Gateway
        payment_tx = MockPaymentGateway.process_payment(
            user=user,
            amount=total_amount,
            payment_token=payment_token,
            idempotency_key=idempotency_key
        )

        if payment_tx.status != 'success':
            raise PaymentDeclinedException(payment_tx.gateway_message, tx=payment_tx)

        # 6. Deduct inventory safely
        for item in cart_items:
            product = locked_products[item.product_id]
            product.stock -= item.quantity
            product.save(update_fields=['stock', 'updated_at'])

        # 7. Create Order & snapshot item prices
        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            status='paid',
            payment_transaction=payment_tx,
            shipping_address=shipping_address or getattr(user, 'address', '') or 'Standard Shipping Address'
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_title=item.product.title,
                unit_price=item.product.price,
                quantity=item.quantity,
                subtotal=item.product.price * item.quantity
            )

        # 8. Clear Cart
        cart.items.all().delete()

        return order
