from django.urls import include, path

urlpatterns = [
    path("auth/", include("apps.authentication.urls")),
    path("guest/", include("apps.guests.urls")),
    path("brands/", include("apps.brands.urls")),
    path("templates/", include("apps.templates.urls")),
    path("usage/", include("apps.usage.urls")),
]
