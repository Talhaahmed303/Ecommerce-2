from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'title', 'slug', 'description', 'price',
            'stock', 'in_stock', 'sku', 'category', 'image_url', 'is_active', 'created_at'
        )

    def get_in_stock(self, obj):
        return obj.stock > 0

class ProductStockUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'stock', 'price', 'is_active')

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price cannot be negative.")
        return value
