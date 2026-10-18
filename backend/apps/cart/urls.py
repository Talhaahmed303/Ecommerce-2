from django.urls import path
from .views import CartView, AddToCartView, UpdateCartItemView, ClearCartView

urlpatterns = [
    path('', CartView.as_view(), name='cart_detail'),
    path('add/', AddToCartView.as_view(), name='cart_add'),
    path('item/<int:item_id>/', UpdateCartItemView.as_view(), name='cart_item_update'),
    path('clear/', ClearCartView.as_view(), name='cart_clear'),
]
