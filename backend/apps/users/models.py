from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone = models.CharField(max_length=30, blank=True, default='')
    address = models.TextField(blank=True, default='')

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_store_admin(self):
        return self.role == 'admin' or self.is_staff or self.is_superuser
