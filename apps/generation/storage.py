from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from django.conf import settings


class LocalObjectStorage:
    def save_bytes(self, *, content: bytes, extension: str, prefix: str | None = None) -> str:
        base_dir = Path(settings.MEDIA_ROOT) / (prefix or settings.OBJECT_STORAGE_MEDIA_PREFIX)
        base_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid4().hex}.{extension.lstrip('.')}"
        path = base_dir / filename
        path.write_bytes(content)
        return f"{settings.MEDIA_URL.rstrip('/')}/{(prefix or settings.OBJECT_STORAGE_MEDIA_PREFIX)}/{filename}"


def get_storage_backend() -> LocalObjectStorage:
    return LocalObjectStorage()
