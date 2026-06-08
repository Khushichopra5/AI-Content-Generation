from rest_framework import permissions, response, status
from rest_framework.views import APIView

from apps.guests.serializers import GuestBootstrapRequestSerializer, GuestSessionSerializer
from apps.guests.services import GuestSessionService


class GuestBootstrapView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes: list[type] = []

    def post(self, request):
        serializer = GuestBootstrapRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = GuestSessionService()
        guest_session = service.bootstrap(**serializer.validated_data)
        limits = service.summarize_limits(guest_session=guest_session)
        return response.Response(
            {
                "session": GuestSessionSerializer(guest_session).data,
                "limits": {
                    "brands_used": limits.brands_used,
                    "templates_used": limits.templates_used,
                    "generations_used": limits.generations_used,
                    "brands_soft_limit": limits.brands_soft_limit,
                    "templates_soft_limit": limits.templates_soft_limit,
                    "generations_soft_limit": limits.generations_soft_limit,
                },
                "capabilities": {
                    "guest_first": True,
                    "auth_optional": True,
                },
            },
            status=status.HTTP_201_CREATED,
        )
