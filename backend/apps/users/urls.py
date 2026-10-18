from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import CustomTokenObtainPairView, RegisterView, ProfileView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='ecom_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='ecom_login'),
    path('refresh/', TokenRefreshView.as_view(), name='ecom_refresh'),
    path('profile/', ProfileView.as_view(), name='ecom_profile'),
]
