from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI


class OpenAITransientError(Exception):
    pass


class OpenAIResponseValidationError(Exception):
    pass


@dataclass(slots=True)
class TextGenerationResult:
    payload: dict[str, Any]
    usage: dict[str, Any]
    response_id: str | None


@dataclass(slots=True)
class ImageGenerationResult:
    image_bytes: bytes
    mime_type: str
    revised_prompt: str | None
    response_id: str | None


class OpenAIClient:
    def __init__(self) -> None:
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            timeout=settings.OPENAI_REQUEST_TIMEOUT,
        )

    def generate_structured_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema: dict[str, Any],
        model: str | None = None,
    ) -> TextGenerationResult:
        try:
            response = self.client.responses.create(
                model=model or settings.OPENAI_TEXT_MODEL,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "marketing_content_payload",
                        "schema": schema,
                        "strict": True,
                    }
                },
            )
        except (APIConnectionError, APITimeoutError, APIStatusError) as exc:
            raise OpenAITransientError(str(exc)) from exc

        if not getattr(response, "output_text", None):
            raise OpenAIResponseValidationError("Model returned empty structured output.")

        try:
            payload = json.loads(response.output_text)
        except json.JSONDecodeError as exc:
            raise OpenAIResponseValidationError("Model returned invalid JSON.") from exc

        return TextGenerationResult(
            payload=payload,
            usage=_coerce_usage(getattr(response, "usage", None)),
            response_id=getattr(response, "id", None),
        )

    def generate_image(
        self,
        *,
        prompt: str,
        model: str | None = None,
    ) -> ImageGenerationResult:
        try:
            response = self.client.images.generate(
                model=model or settings.OPENAI_IMAGE_MODEL,
                prompt=prompt,
                output_format="png",
                quality="medium",
                size="1024x1024",
                timeout=settings.OPENAI_IMAGE_REQUEST_TIMEOUT,
            )
        except (APIConnectionError, APITimeoutError, APIStatusError) as exc:
            raise OpenAITransientError(str(exc)) from exc

        if getattr(response, "data", None):
            image_entry = response.data[0]
            if getattr(image_entry, "b64_json", None):
                return ImageGenerationResult(
                    image_bytes=base64.b64decode(image_entry.b64_json),
                    mime_type="image/png",
                    revised_prompt=None,
                    response_id=None,
                )

        raise OpenAIResponseValidationError("Image generation output missing image payload.")


def _coerce_usage(usage: Any) -> dict[str, Any]:
    if usage is None:
        return {}
    if isinstance(usage, dict):
        return usage
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    return {
        key: value
        for key, value in usage.__dict__.items()
        if not key.startswith("_")
    }
