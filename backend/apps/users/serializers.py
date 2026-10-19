from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from .models import SafeUsernameValidator
import re

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'phone', 'address', 'date_joined')
        read_only_fields = ('id', 'date_joined')

class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=[
            SafeUsernameValidator(),
            UniqueValidator(queryset=User.objects.all(), message='A user with that username already exists.')
        ]
    )
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role', 'phone', 'address')

    def validate_username(self, value):
        cleaned = re.sub(r'\s+', ' ', value).strip()
        if not cleaned:
            raise serializers.ValidationError("Username cannot be empty.")
        if User.objects.filter(username__iexact=cleaned).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return cleaned

    def create(self, validated_data):
        role = validated_data.get('role', 'customer')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=role,
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', '')
        )
        if role == 'admin':
            user.is_staff = True
            user.save()
        return user
