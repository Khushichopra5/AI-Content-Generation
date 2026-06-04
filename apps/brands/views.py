from rest_framework import filters, permissions, viewsets
from rest_framework.authentication import SessionAuthentication

from apps.authentication.authentication import BearerTokenAuthentication

from .models import BrandProfile
from .serializers import BrandProfileSerializer


class BrandProfileViewSet(viewsets.ModelViewSet):
    serializer_class = BrandProfileSerializer
    authentication_classes = [SessionAuthentication, BearerTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["brand_name", "product_description", "target_audience"]
    ordering_fields = ["brand_name", "created_at", "updated_at"]
    ordering = ["brand_name"]

    def get_queryset(self):
        queryset = BrandProfile.objects.select_related("user")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def perform_create(self, serializer: BrandProfileSerializer) -> None:
        serializer.save(user=self.request.user)
