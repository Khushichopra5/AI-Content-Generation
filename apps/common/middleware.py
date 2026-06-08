from __future__ import annotations

import uuid

from django.conf import settings
from django.http import HttpResponse


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        response = self.get_response(request)
        response["X-Request-ID"] = request.request_id
        return response


class CORSMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin")
        if request.method == "OPTIONS" and self._is_allowed_origin(origin):
            response = HttpResponse(status=200)
        else:
            response = self.get_response(request)

        if self._is_allowed_origin(origin):
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Methods"] = ", ".join(settings.CORS_ALLOW_METHODS)
            response["Access-Control-Allow-Headers"] = ", ".join(settings.CORS_ALLOW_HEADERS)
            response["Access-Control-Max-Age"] = str(settings.CORS_PREFLIGHT_MAX_AGE_SECONDS)
            response["Vary"] = "Origin"
        return response

    def _is_allowed_origin(self, origin: str | None) -> bool:
        if not origin:
            return False
        if settings.CORS_ALLOW_ALL_ORIGINS:
            return True
        return origin in settings.CORS_ALLOWED_ORIGINS
