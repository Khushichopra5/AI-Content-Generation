from rest_framework import filters, permissions, viewsets
from rest_framework.authentication import SessionAuthentication

from apps.authentication.authentication import BearerTokenAuthentication

from .models import UsageEvent
from .serializers import UsageEventSerializer


class UsageEventViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UsageEventSerializer
    authentication_classes = [SessionAuthentication, BearerTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["event_type"]
    ordering_fields = ["created_at", "tokens_in", "tokens_out", "latency_ms"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = UsageEvent.objects.select_related("user")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)
