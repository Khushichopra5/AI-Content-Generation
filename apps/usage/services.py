from __future__ import annotations

from typing import Any

from apps.usage.models import UsageEvent


class UsageEventService:
    def record_generation_usage(
        self,
        *,
        user,
        event_type: str,
        usage: dict[str, Any],
        cache_hit: bool,
    ) -> UsageEvent:
        input_tokens = usage.get("input_tokens", 0) or usage.get("prompt_tokens", 0) or 0
        output_tokens = usage.get("output_tokens", 0) or usage.get("completion_tokens", 0) or 0
        return UsageEvent.objects.create(
            user=user,
            event_type=event_type,
            tokens_in=input_tokens,
            tokens_out=output_tokens,
            latency_ms=usage.get("total_latency_ms", 0) or 0,
            cache_hit=cache_hit,
            metadata=usage,
        )
