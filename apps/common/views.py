from django.conf import settings
from django.core.cache import caches
from django.db import connection
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


def home_view(request):
    return render(
        request,
        "home.html",
        {
            "debug": settings.DEBUG,
        },
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def healthcheck_view(request):
    db_ok = False
    redis_ok = False

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        db_ok = True
    except Exception:
        db_ok = False

    try:
        cache = caches["default"]
        cache.set("healthcheck", "ok", timeout=5)
        redis_ok = cache.get("healthcheck") == "ok"
    except Exception:
        redis_ok = False

    status_code = 200 if db_ok and redis_ok else 503
    return Response(
        {
            "status": "ok" if status_code == 200 else "degraded",
            "database": db_ok,
            "redis": redis_ok,
            "debug": settings.DEBUG,
        },
        status=status_code,
    )
