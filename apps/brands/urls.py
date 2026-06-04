from rest_framework.routers import DefaultRouter

from apps.brands.views import BrandProfileViewSet

router = DefaultRouter()
router.register("", BrandProfileViewSet, basename="brand-profile")

urlpatterns = router.urls
