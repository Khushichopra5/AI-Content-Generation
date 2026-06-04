from __future__ import annotations

import hashlib
import json
import uuid
from datetime import date, datetime
from typing import Any


def normalize_generation_payload(payload: dict[str, Any]) -> dict[str, Any]:
    def normalize(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: normalize(value[key]) for key in sorted(value)}
        if isinstance(value, list):
            return [normalize(item) for item in value]
        if isinstance(value, str):
            return " ".join(value.strip().split())
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        return value

    return normalize(payload)


def build_prompt_hash(payload: dict[str, Any]) -> str:
    normalized = normalize_generation_payload(payload)
    serialized = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
