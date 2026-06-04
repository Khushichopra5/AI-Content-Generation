from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.generation.views import (
    GenerationCreateView,
    GenerationJobViewSet,
    ImageGenerationCreateView,
    RegenerateView,
)

router = DefaultRouter()
router.register("jobs", GenerationJobViewSet, basename="generation-job")

urlpatterns = [
    path("generate/", GenerationCreateView.as_view(), name="generate"),
    path("generate/image/", ImageGenerationCreateView.as_view(), name="generate-image"),
    path("regenerate/<uuid:job_id>/", RegenerateView.as_view(), name="regenerate"),
]

urlpatterns += router.urls
