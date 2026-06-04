import uuid

from django.conf import settings
from django.db import models


class ContentChannel(models.TextChoices):
    SOCIAL = "social", "Social"
    ADS = "ads", "Ads"
    EMAIL = "email", "Email"
    LANDING_PAGE = "landing_page", "Landing Page"
    CAMPAIGN = "campaign", "Campaign"


class ContentObjective(models.TextChoices):
    LEAD_GENERATION = "lead_generation", "Lead Generation"
    AWARENESS = "awareness", "Awareness"
    CONVERSION = "conversion", "Conversion"
    RETENTION = "retention", "Retention"
    PRODUCT_LAUNCH = "product_launch", "Product Launch"


class ContentTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="content_templates")
    name = models.CharField(max_length=255)
    channel = models.CharField(max_length=32, choices=ContentChannel.choices)
    objective = models.CharField(max_length=32, choices=ContentObjective.choices)
    prompt_template = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name", "created_at")
        unique_together = ("user", "name")
        indexes = [
            models.Index(fields=("user", "channel")),
            models.Index(fields=("user", "objective")),
        ]

    def __str__(self) -> str:
        return self.name

