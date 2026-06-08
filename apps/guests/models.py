from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel, UUIDPrimaryKeyModel


class GuestSessionStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    CONVERTED = "converted", "Converted"
    EXPIRED = "expired", "Expired"


class GuestSession(UUIDPrimaryKeyModel, TimeStampedModel):
    guest_id = models.CharField(max_length=64, unique=True)
    session_id = models.CharField(max_length=64, unique=True)
    device_id = models.CharField(max_length=64, db_index=True)
    backing_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="guest_session",
    )
    claimed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="claimed_guest_sessions",
    )
    status = models.CharField(
        max_length=16,
        choices=GuestSessionStatus.choices,
        default=GuestSessionStatus.ACTIVE,
    )
    preferences = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    last_seen_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ("-last_seen_at",)
        indexes = [
            models.Index(fields=("device_id", "status")),
            models.Index(fields=("expires_at",)),
        ]

    @property
    def is_active(self) -> bool:
        return self.status == GuestSessionStatus.ACTIVE and self.expires_at > timezone.now()

    def touch(self, *, ttl_seconds: int) -> None:
        self.last_seen_at = timezone.now()
        self.expires_at = self.last_seen_at + timedelta(seconds=ttl_seconds)
        self.save(update_fields=["last_seen_at", "expires_at", "updated_at"])
