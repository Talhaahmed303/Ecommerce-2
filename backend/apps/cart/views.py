from rest_framework import views, permissions, status
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer, CartItemSerializer
from apps.products.models import Product

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    # Anonymous session cart
    if not request.session.session_key:
        request.session.create()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart

class CartView(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CartSerializer

    def get(self, request):
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response({
            "success": True,
            "data": serializer.data
        })

class AddToCartView(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = AddToCartSerializer

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {"success": False, "message": "Product not found or inactive."},
                status=status.HTTP_404_NOT_FOUND
            )

        if product.stock < 1:
            return Response(
                {"success": False, "message": f"Sorry, '{product.title}' is currently out of stock."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        target_quantity = quantity if created else cart_item.quantity + quantity
        if target_quantity > product.stock:
            return Response(
                {
                    "success": False,
                    "message": f"Cannot add {quantity} units. Only {product.stock} units available in stock (you have {cart_item.quantity} in cart)."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = target_quantity
        cart_item.save()

        return Response({
            "success": True,
            "message": f"Added {quantity}x '{product.title}' to your cart.",
            "data": CartSerializer(cart).data
        }, status=status.HTTP_200_OK)

class UpdateCartItemView(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CartItemSerializer

    def patch(self, request, item_id):
        cart = get_or_create_cart(request)
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"success": False, "message": "Cart item not found."}, status=status.HTTP_404_NOT_FOUND)

        new_qty = request.data.get('quantity')
        if new_qty is None or int(new_qty) < 1:
            cart_item.delete()
            return Response({"success": True, "message": "Item removed from cart.", "data": CartSerializer(cart).data})

        new_qty = int(new_qty)
        if new_qty > cart_item.product.stock:
            return Response(
                {"success": False, "message": f"Cannot exceed available stock ({cart_item.product.stock})."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = new_qty
        cart_item.save()
        return Response({"success": True, "data": CartSerializer(cart).data})

    def delete(self, request, item_id):
        cart = get_or_create_cart(request)
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
        except CartItem.DoesNotExist:
            pass
        return Response({"success": True, "message": "Item removed.", "data": CartSerializer(cart).data})

class ClearCartView(views.APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CartSerializer

    def post(self, request):
        cart = get_or_create_cart(request)
        cart.items.all().delete()
        return Response({"success": True, "message": "Cart cleared.", "data": CartSerializer(cart).data})
