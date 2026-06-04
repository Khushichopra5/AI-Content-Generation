import hashlib
import secrets
import uuid
from dataclasses import dataclass
from typing import Final

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


TOKEN_PREFIX: Final[str] = "cgt"


class UserRole(models.TextChoices):
    ADMIN = "admin", "Admin"
    MEMBER = "member", "Member"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields: object) -> "User":
        if not email:
            raise ValueError("The email address must be provided.")
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.full_clean(exclude={"password"})
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields: object) -> "User":
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", UserRole.MEMBER)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: object,
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", UserRole.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=False, blank=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=32, choices=UserRole.choices, default=UserRole.MEMBER)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.email


@dataclass(frozen=True)
class IssuedToken:
    key: str
    token: "APIToken"


class APIToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE, related_name="api_tokens")
    name = models.CharField(max_length=100, default="default")
    prefix = models.CharField(max_length=12, editable=False)
    key_digest = models.CharField(max_length=64, unique=True, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("user", "revoked_at")),
            models.Index(fields=("expires_at",)),
        ]

    def __str__(self) -> str:
        return f"{self.user.email}::{self.name}"

    @property
    def is_active(self) -> bool:
        if self.revoked_at is not None:
            return False
        if self.expires_at is not None and self.expires_at <= timezone.now():
            return False
        return True

    @classmethod
    def issue_for_user(
        cls,
        user: User,
        *,
        name: str = "default",
        expires_at: timezone.datetime | None = None,
    ) -> IssuedToken:
        raw_secret = secrets.token_urlsafe(32)
        token_key = f"{TOKEN_PREFIX}_{raw_secret}"
        token = cls.objects.create(
            user=user,
            name=name,
            prefix=token_key[:12],
            key_digest=cls.build_digest(token_key),
            expires_at=expires_at,
        )
        return IssuedToken(key=token_key, token=token)

    @staticmethod
    def build_digest(raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

    def touch(self) -> None:
        self.last_used_at = timezone.now()
        self.save(update_fields=["last_used_at"])

    def revoke(self) -> None:
        if self.revoked_at is None:
            self.revoked_at = timezone.now()
            self.save(update_fields=["revoked_at"])
