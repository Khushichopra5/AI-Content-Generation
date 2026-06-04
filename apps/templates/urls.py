from rest_framework.routers import DefaultRouter

from apps.templates.views import ContentTemplateViewSet

router = DefaultRouter()
router.register("", ContentTemplateViewSet, basename="content-template")

urlpatterns = router.urls
