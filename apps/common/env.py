from __future__ import annotations

import os


class Env:
    def str(self, key: str, default: str | None = None) -> str:
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        return value

    def bool(self, key: str, default: bool = False) -> bool:
        value = os.getenv(key)
        if value is None:
            return default
        return value.lower() in {"1", "true", "yes", "on"}

    def int(self, key: str, default: int) -> int:
        value = os.getenv(key)
        return int(value) if value is not None else default

    def list(self, key: str, default: list[str] | None = None) -> list[str]:
        value = os.getenv(key)
        if value is None:
            return default or []
        return [item.strip() for item in value.split(",") if item.strip()]


env = Env()
