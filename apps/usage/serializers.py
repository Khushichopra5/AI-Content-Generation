from rest_framework import serializers

from .models import UsageEvent


class UsageEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageEvent
        fields = (
            "id",
            "user",
            "event_type",
            "tokens_in",
            "tokens_out",
            "latency_ms",
            "cache_hit",
            "metadata",
            "created_at",
        )
        read_only_fields = fields
