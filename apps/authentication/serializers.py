from django.contrib.auth import authenticate, password_validation
from django.utils import timezone
from rest_framework import serializers

from .models import APIToken, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "name", "role", "created_at", "updated_at")
        read_only_fields = ("id", "role", "created_at", "updated_at")


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("id", "email", "name", "password")
        read_only_fields = ("id",)

    def validate_password(self, value: str) -> str:
        password_validation.validate_password(value)
        return value

    def create(self, validated_data: dict[str, object]) -> User:
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    token_name = serializers.CharField(required=False, default="default", max_length=100)

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        request = self.context.get("request")
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(request=request, username=email, password=password)
        if user is None:
            raise serializers.ValidationError("Invalid email/password combination.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        if user.is_guest:
            raise serializers.ValidationError("Guest identities cannot log in directly.")
        attrs["user"] = user
        return attrs


class TokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField(read_only=True)
    expires_at = serializers.DateTimeField(allow_null=True, read_only=True)
    user = UserSerializer(read_only=True)


class APITokenSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = APIToken
        fields = (
            "id",
            "name",
            "prefix",
            "created_at",
            "last_used_at",
            "expires_at",
            "revoked_at",
            "is_active",
        )
        read_only_fields = ("id", "prefix", "created_at", "last_used_at", "revoked_at", "is_active")

    def validate_expires_at(self, value: timezone.datetime | None) -> timezone.datetime | None:
        if value is not None and value <= timezone.now():
            raise serializers.ValidationError("Expiration must be in the future.")
        return value


class APITokenCreateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, default="default", max_length=100)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate_expires_at(self, value: timezone.datetime | None) -> timezone.datetime | None:
        if value is not None and value <= timezone.now():
            raise serializers.ValidationError("Expiration must be in the future.")
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("name",)
