from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from apps.guests.services import GuestSessionService


class GuestSessionAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        guest_id = request.headers.get("X-Guest-Id")
        session_id = request.headers.get("X-Session-Id")
        device_id = request.headers.get("X-Device-Id")
        if not guest_id and not session_id:
            return None
        if not guest_id or not session_id or not device_id:
            raise AuthenticationFailed("Guest session headers are incomplete.")

        guest_session = GuestSessionService().resolve_session(
            guest_id=guest_id,
            session_id=session_id,
            device_id=device_id,
        )
        if guest_session is None:
            raise AuthenticationFailed("Guest session is invalid or expired.")

        request.guest_session = guest_session
        return (guest_session.backing_user, guest_session)
