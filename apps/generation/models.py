from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel, UUIDPrimaryKeyModel
from apps.generation.constants import ASSET_TYPES, JOB_STATUS


class GenerationJob(UUIDPrimaryKeyModel, TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="generation_jobs",
    )
    brand_profile = models.ForeignKey(
        "brands.BrandProfile",
        on_delete=models.CASCADE,
        related_name="generation_jobs",
    )
    template = models.ForeignKey(
        "templates.ContentTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generation_jobs",
    )
    input_payload = models.JSONField()
    prompt_hash = models.CharField(max_length=64, db_index=True)
    status = models.CharField(max_length=16, choices=JOB_STATUS, default="queued")
    model_name = models.CharField(max_length=100, blank=True)
    output_payload = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    cache_hit = models.BooleanField(default=False)
    include_image = models.BooleanField(default=False)
    moderation_notes = models.JSONField(default=list, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["user", "prompt_hash", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.id} ({self.status})"


class Asset(UUIDPrimaryKeyModel, TimeStampedModel):
    generation_job = models.ForeignKey(
        GenerationJob,
        on_delete=models.CASCADE,
        related_name="assets",
    )
    asset_type = models.CharField(max_length=16, choices=ASSET_TYPES)
    storage_url = models.URLField(max_length=500)
    mime_type = models.CharField(max_length=100)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"{self.asset_type}:{self.generation_job_id}"
