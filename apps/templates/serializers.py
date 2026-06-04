from rest_framework import serializers

from .models import ContentTemplate


class ContentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentTemplate
        fields = (
            "id",
            "user",
            "name",
            "channel",
            "objective",
            "prompt_template",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "created_at", "updated_at")
