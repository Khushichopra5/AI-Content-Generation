from rest_framework import serializers

from .models import BrandProfile


class BrandProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandProfile
        fields = (
            "id",
            "user",
            "brand_name",
            "brand_voice",
            "banned_phrases",
            "preferred_tone",
            "example_copy",
            "product_description",
            "target_audience",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "created_at", "updated_at")

    def validate_banned_phrases(self, value: object) -> list[str]:
        if not isinstance(value, list):
            raise serializers.ValidationError("Banned phrases must be a list of strings.")
        cleaned: list[str] = []
        for item in value:
            if not isinstance(item, str) or not item.strip():
                raise serializers.ValidationError("Each banned phrase must be a non-empty string.")
            cleaned.append(item.strip())
        return cleaned
