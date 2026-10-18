from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer, ProductStockUpdateSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and (getattr(request.user, 'role', '') == 'admin' or request.user.is_staff)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'id'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'category', 'sku']
    ordering_fields = ['price', 'created_at', 'stock', 'title']
    ordering = ['title']

    def get_serializer_class(self):
        if self.action in ['update_stock', 'partial_update'] and (getattr(self.request.user, 'role', '') == 'admin' or self.request.user.is_staff):
            return ProductStockUpdateSerializer
        return ProductSerializer

    def get_queryset(self):
        qs = Product.objects.all()
        # Non-admins only see active products
        user = self.request.user
        if not user or not user.is_authenticated or getattr(user, 'role', '') != 'admin':
            qs = qs.filter(is_active=True)

        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category)

        in_stock = self.request.query_params.get('in_stock')
        if in_stock == 'true':
            qs = qs.filter(stock__gt=0)

        return qs

    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAdminUser])
    def update_stock(self, request, id=None):
        product = self.get_object()
        serializer = ProductStockUpdateSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "success": True,
            "message": "Product stock updated successfully",
            "data": ProductSerializer(product).data
        })
