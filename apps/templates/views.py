from rest_framework import filters, permissions, viewsets
from rest_framework.authentication import SessionAuthentication

from apps.authentication.authentication import BearerTokenAuthentication
from apps.guests.authentication import GuestSessionAuthentication

from .models import ContentTemplate
from .serializers import ContentTemplateSerializer


class ContentTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = ContentTemplateSerializer
    authentication_classes = [SessionAuthentication, BearerTokenAuthentication, GuestSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "prompt_template", "channel", "objective"]
    ordering_fields = ["name", "channel", "objective", "created_at", "updated_at"]
    ordering = ["name"]

    def get_queryset(self):
        queryset = ContentTemplate.objects.select_related("user")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer: ContentTemplateSerializer) -> None:
        serializer.save(user=self.request.user)
