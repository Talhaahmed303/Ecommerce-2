from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CheckoutView

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('orders/checkout/', CheckoutView.as_view(), name='order_checkout'),
    path('', include(router.urls)),
]
