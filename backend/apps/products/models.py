from django.db import models
from django.utils.text import slugify

class Product(models.Model):
    CATEGORY_CHOICES = (
        ('electronics', 'Consumer Electronics'),
        ('audio', 'Audio & Acoustics'),
        ('accessories', 'Developer Gear & Accessories'),
        ('ergonomics', 'Workstation Ergonomics'),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=50, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='electronics')
    image_url = models.URLField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        constraints = [
            models.CheckConstraint(
                check=models.Q(stock__gte=0),
                name='prevent_negative_stock_constraint'
            ),
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='prevent_negative_price_constraint'
            ),
        ]
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['stock']),
            models.Index(fields=['sku']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} [SKU: {self.sku}] - ${self.price} (Stock: {self.stock})"
