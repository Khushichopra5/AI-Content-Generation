import uuid

from django.conf import settings
from django.db import models


class BrandProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="brand_profiles")
    brand_name = models.CharField(max_length=255)
    brand_voice = models.TextField()
    banned_phrases = models.JSONField(default=list, blank=True)
    preferred_tone = models.CharField(max_length=64)
    example_copy = models.TextField(blank=True)
    product_description = models.TextField()
    target_audience = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("brand_name", "created_at")
        unique_together = ("user", "brand_name")
        indexes = [
            models.Index(fields=("user", "brand_name")),
            models.Index(fields=("created_at",)),
        ]

    def __str__(self) -> str:
        return self.brand_name

