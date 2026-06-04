import uuid

from django.conf import settings
from django.db import models


class UsageEventType(models.TextChoices):
    GENERATE_TEXT = "generate_text", "Generate Text"
    GENERATE_IMAGE = "generate_image", "Generate Image"
    CACHE_HIT = "cache_hit", "Cache Hit"
    CACHE_MISS = "cache_miss", "Cache Miss"
    LOGIN = "login", "Login"


class UsageEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="usage_events")
    event_type = models.CharField(max_length=32, choices=UsageEventType.choices)
    tokens_in = models.PositiveIntegerField(default=0)
    tokens_out = models.PositiveIntegerField(default=0)
    latency_ms = models.PositiveIntegerField(default=0)
    cache_hit = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("user", "event_type")),
            models.Index(fields=("created_at",)),
        ]

    def __str__(self) -> str:
        return f"{self.user_id}:{self.event_type}"

