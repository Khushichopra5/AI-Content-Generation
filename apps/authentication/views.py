from django.contrib.auth import login, logout
from django.db import transaction
from rest_framework import generics, permissions, response, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.common.throttling import AnonymousRateThrottle
from apps.guests.authentication import GuestSessionAuthentication
from apps.guests.services import GuestSessionService

from .authentication import BearerTokenAuthentication
from .models import APIToken, User
from .permissions import IsSelfOrAdmin
from .serializers import (
    APITokenCreateSerializer,
    APITokenSerializer,
    LoginSerializer,
    TokenResponseSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class RegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = [SessionAuthentication]
    throttle_classes = [AnonymousRateThrottle]

    @transaction.atomic
    def post(self, request: Request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        _migrate_guest_session_if_present(request=request, target_user=user)
        issued_token = APIToken.issue_for_user(user, name="signup")
        return response.Response(
            {
                "user": UserSerializer(user).data,
                "token": issued_token.key,
                "expires_at": issued_token.token.expires_at,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = [SessionAuthentication]
    throttle_classes = [AnonymousRateThrottle]

    @transaction.atomic
    def post(self, request: Request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        _migrate_guest_session_if_present(request=request, target_user=user)
        login(request, user)
        issued_token = APIToken.issue_for_user(user, name=serializer.validated_data["token_name"])
        payload = {
            "token": issued_token.key,
            "expires_at": issued_token.token.expires_at,
            "user": UserSerializer(user).data,
        }
        return response.Response(TokenResponseSerializer(payload).data)


class LogoutView(APIView):
    authentication_classes = [SessionAuthentication, BearerTokenAuthentication, GuestSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request):
        if isinstance(request.auth, APIToken):
            request.auth.revoke()
        logout(request)
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = [SessionAuthentication, BearerTokenAuthentication, GuestSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsSelfOrAdmin]

    def get_object(self) -> User:
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserUpdateSerializer
        return UserSerializer

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return response.Response(UserSerializer(self.get_object()).data)


class APITokenViewSet(viewsets.ModelViewSet):
    serializer_class = APITokenSerializer
    authentication_classes = [SessionAuthentication, BearerTokenAuthentication, GuestSessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        queryset = APIToken.objects.select_related("user")
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return APITokenCreateSerializer
        return APITokenSerializer

    def create(self, request: Request, *args, **kwargs):
        if request.user.is_guest:
            return response.Response(
                {"detail": "Guest sessions cannot mint permanent API tokens. Create an account first."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        issued_token = APIToken.issue_for_user(
            request.user,
            name=serializer.validated_data["name"],
            expires_at=serializer.validated_data.get("expires_at"),
        )
        return response.Response(
            {
                "token": issued_token.key,
                "expires_at": issued_token.token.expires_at,
                "token_record": APITokenSerializer(issued_token.token).data,
            },
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request: Request, *args, **kwargs):
        token = self.get_object()
        token.revoke()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def revoke(self, request: Request, pk=None):
        token = self.get_object()
        token.revoke()
        return response.Response(APITokenSerializer(token).data)


def _resolve_guest_session_from_headers(request: Request):
    guest_id = request.headers.get("X-Guest-Id")
    session_id = request.headers.get("X-Session-Id")
    device_id = request.headers.get("X-Device-Id")
    if not guest_id or not session_id or not device_id:
        return None
    return GuestSessionService().resolve_session(
        guest_id=guest_id,
        session_id=session_id,
        device_id=device_id,
    )


def _migrate_guest_session_if_present(*, request: Request, target_user: User) -> None:
    guest_session = _resolve_guest_session_from_headers(request)
    if guest_session is None:
        return
    GuestSessionService().migrate_guest_assets(guest_session=guest_session, target_user=target_user)
