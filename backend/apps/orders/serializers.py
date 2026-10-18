from rest_framework import serializers
from .models import Order, OrderItem
from apps.users.serializers import UserSerializer
from apps.payments.models import PaymentTransaction

class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ('idempotency_key', 'amount', 'payment_token', 'status', 'gateway_message', 'created_at')

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_title', 'unit_price', 'quantity', 'subtotal')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    payment_transaction = PaymentTransactionSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'order_number', 'user', 'total_amount', 'status',
            'shipping_address', 'payment_transaction', 'items', 'created_at', 'updated_at'
        )

class CheckoutRequestSerializer(serializers.Serializer):
    payment_token = serializers.CharField(default='tok_success')
    idempotency_key = serializers.CharField(required=True)
    shipping_address = serializers.CharField(required=False, allow_blank=True)

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',)

    def validate_status(self, value):
        order = self.instance
        if not order.can_transition_to(value):
            raise serializers.ValidationError(
                f"Invalid status transition from '{order.status}' to '{value}'. Allowed: {order.VALID_TRANSITIONS.get(order.status, [])}"
            )
        return value
