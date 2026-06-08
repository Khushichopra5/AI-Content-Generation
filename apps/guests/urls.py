from django.urls import path

from apps.guests.views import GuestBootstrapView

urlpatterns = [
    path("bootstrap/", GuestBootstrapView.as_view(), name="guest-bootstrap"),
]
