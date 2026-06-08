from rest_framework import serializers

from apps.guests.models import GuestSession


class GuestBootstrapRequestSerializer(serializers.Serializer):
    guest_id = serializers.CharField(required=False, allow_blank=False, max_length=64)
    session_id = serializers.CharField(required=False, allow_blank=False, max_length=64)
    device_id = serializers.CharField(required=False, allow_blank=False, max_length=64)


class GuestSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestSession
        fields = (
            "guest_id",
            "session_id",
            "device_id",
            "status",
            "preferences",
            "last_seen_at",
            "expires_at",
        )
        read_only_fields = fields
