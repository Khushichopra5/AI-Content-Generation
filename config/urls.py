from django.contrib import admin
from django.urls import include, path

from apps.common.views import healthcheck_view, home_view

urlpatterns = [
    path("", home_view, name="home"),
    path("admin/", admin.site.urls),
    path("health/", healthcheck_view, name="healthcheck"),
    path("api/v1/", include("apps.api_urls")),
    path("api/v1/", include("apps.generation.urls")),
]
