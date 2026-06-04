from rest_framework.routers import DefaultRouter
from django.urls import path

from apps.authentication.views import APITokenViewSet, LoginView, LogoutView, MeView, RegistrationView

router = DefaultRouter()
router.register("tokens", APITokenViewSet, basename="api-token")

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
]

urlpatterns += router.urls
