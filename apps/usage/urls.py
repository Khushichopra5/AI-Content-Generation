from rest_framework.routers import DefaultRouter

from apps.usage.views import UsageEventViewSet

router = DefaultRouter()
router.register("", UsageEventViewSet, basename="usage-event")

urlpatterns = router.urls
