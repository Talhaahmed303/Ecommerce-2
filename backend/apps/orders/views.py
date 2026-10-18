from rest_framework import viewsets, permissions, status, views
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order
from .serializers import OrderSerializer, CheckoutRequestSerializer, OrderStatusUpdateSerializer
from .services import checkout_cart, InsufficientStockException, PaymentDeclinedException, EmptyCartException

class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'role', '') == 'admin' or user.is_staff or user.is_superuser:
            return Order.objects.all().select_related('user', 'payment_transaction').prefetch_related('items__product')
        return Order.objects.filter(user=user).select_related('user', 'payment_transaction').prefetch_related('items__product')

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, id=None):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "success": True,
            "message": f"Order {order.order_number} status updated to {order.status}",
            "data": OrderSerializer(order).data
        })

class CheckoutView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CheckoutRequestSerializer

    def post(self, request):
        serializer = CheckoutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data.get('payment_token', 'tok_success')
        idempotency_key = serializer.validated_data['idempotency_key']
        shipping_address = serializer.validated_data.get('shipping_address', '')

        try:
            order = checkout_cart(
                user=request.user,
                payment_token=token,
                idempotency_key=idempotency_key,
                shipping_address=shipping_address
            )
            return Response({
                "success": True,
                "message": "Order placed and payment settled successfully!",
                "data": OrderSerializer(order).data
            }, status=status.HTTP_201_CREATED)

        except EmptyCartException as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except InsufficientStockException as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_409_CONFLICT)
        except PaymentDeclinedException as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_402_PAYMENT_REQUIRED)
        except Exception as e:
            return Response({"success": False, "message": f"Checkout error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
