from typing import Optional

from django.utils.translation import gettext_lazy as _
from rest_framework import authentication, exceptions

from .models import APIToken


class BearerTokenAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request) -> Optional[tuple[object, APIToken]]:
        header = authentication.get_authorization_header(request).decode("utf-8")
        if not header:
            return None

        parts = header.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        raw_token = parts[1]
        token = self.get_token(raw_token)
        if token is None:
            raise exceptions.AuthenticationFailed(_("Invalid token."))
        if not token.is_active:
            raise exceptions.AuthenticationFailed(_("Token is inactive."))

        token.touch()
        return (token.user, token)

    def authenticate_header(self, request) -> str:
        return self.keyword

    @staticmethod
    def get_token(raw_token: str) -> APIToken | None:
        digest = APIToken.build_digest(raw_token)
        try:
            return APIToken.objects.select_related("user").get(key_digest=digest)
        except APIToken.DoesNotExist:
            return None

