from __future__ import annotations

from rest_framework import serializers

from apps.generation.constants import GENERATION_CHANNELS
from apps.generation.models import Asset, GenerationJob


class GenerationCreateSerializer(serializers.Serializer):
    brand_profile_id = serializers.UUIDField()
    template_id = serializers.UUIDField(required=False, allow_null=True)
    channel = serializers.ChoiceField(choices=[value for value, _ in GENERATION_CHANNELS])
    objective = serializers.CharField(max_length=100)
    tone = serializers.CharField(max_length=100)
    audience = serializers.CharField(max_length=200)
    product_description = serializers.CharField(max_length=2000)
    key_points = serializers.ListField(
        child=serializers.CharField(max_length=240),
        allow_empty=False,
        min_length=1,
        max_length=10,
    )
    cta = serializers.CharField(max_length=200)
    output_count = serializers.IntegerField(min_value=1, max_value=10)
    include_image = serializers.BooleanField(default=False)
    length = serializers.ChoiceField(choices=["short", "medium", "long"], default="medium")

    def validate(self, attrs):
        brand = self.context["brand_queryset"].filter(id=attrs["brand_profile_id"]).first()
        if not brand:
            raise serializers.ValidationError({"brand_profile_id": "Brand profile not found."})
        attrs["brand_profile"] = brand

        template_id = attrs.get("template_id")
        if template_id:
            template = self.context["template_queryset"].filter(id=template_id).first()
            if not template:
                raise serializers.ValidationError({"template_id": "Template not found."})
            attrs["template"] = template
        else:
            attrs["template"] = None
        return attrs


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ["id", "asset_type", "storage_url", "mime_type", "metadata", "created_at"]


class GenerationJobSerializer(serializers.ModelSerializer):
    assets = AssetSerializer(many=True, read_only=True)

    class Meta:
        model = GenerationJob
        fields = [
            "id",
            "brand_profile_id",
            "template_id",
            "status",
            "model_name",
            "output_payload",
            "error_message",
            "cache_hit",
            "include_image",
            "assets",
            "created_at",
            "updated_at",
            "completed_at",
        ]


class GenerationSubmissionResponseSerializer(serializers.Serializer):
    job_id = serializers.UUIDField()
    status = serializers.CharField()
    cache_hit = serializers.BooleanField()
    deduplicated = serializers.BooleanField()
