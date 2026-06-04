from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone
from jsonschema import ValidationError as JSONSchemaValidationError
from jsonschema import validate

from apps.generation.models import GenerationJob
from apps.generation.prompting import build_prompt_hash, normalize_generation_payload
from apps.generation.schemas import GENERATION_RESPONSE_SCHEMA
from apps.integrations.openai_client import OpenAIClient, OpenAIResponseValidationError
from apps.usage.services import UsageEventService

logger = logging.getLogger(__name__)


class ModerationError(Exception):
    pass


@dataclass(slots=True)
class SubmissionResult:
    job: GenerationJob
    created: bool
    deduplicated: bool


class GenerationService:
    def submit_job(self, *, user, validated_data: dict[str, Any]) -> SubmissionResult:
        brand_profile = validated_data["brand_profile"]
        template = validated_data.get("template")
        generation_payload = {
            "brand_profile": {
                "id": str(brand_profile.id),
                "brand_name": brand_profile.brand_name,
                "brand_voice": brand_profile.brand_voice,
                "banned_phrases": brand_profile.banned_phrases,
                "preferred_tone": brand_profile.preferred_tone,
                "example_copy": brand_profile.example_copy,
                "product_description": brand_profile.product_description,
                "target_audience": brand_profile.target_audience,
                "updated_at": brand_profile.updated_at.isoformat(),
            },
            "template": {
                "id": str(template.id),
                "updated_at": template.updated_at.isoformat(),
                "prompt_template": template.prompt_template,
            }
            if template
            else None,
            "request": {
                key: value
                for key, value in validated_data.items()
                if key not in {"brand_profile", "template"}
            },
            "model": settings.OPENAI_TEXT_MODEL,
        }
        generation_payload = normalize_generation_payload(generation_payload)
        prompt_hash = build_prompt_hash(generation_payload)

        active_job = (
            GenerationJob.objects.select_related("brand_profile", "template")
            .filter(
                user=user,
                prompt_hash=prompt_hash,
                status__in=["queued", "running"],
            )
            .first()
        )
        if active_job:
            return SubmissionResult(job=active_job, created=False, deduplicated=True)

        cached = self.get_cached_result(prompt_hash)
        if cached:
            job = GenerationJob.objects.create(
                user=user,
                brand_profile=brand_profile,
                template=template,
                input_payload=generation_payload,
                prompt_hash=prompt_hash,
                status="succeeded",
                model_name=settings.OPENAI_TEXT_MODEL,
                output_payload=cached,
                cache_hit=True,
                include_image=validated_data.get("include_image", False),
                completed_at=timezone.now(),
            )
            UsageEventService().record_generation_usage(
                user=user,
                event_type="cache_hit",
                usage={},
                cache_hit=True,
            )
            return SubmissionResult(job=job, created=True, deduplicated=False)

        self._run_basic_safety_checks(validated_data)

        job = GenerationJob.objects.create(
            user=user,
            brand_profile=brand_profile,
            template=template,
            input_payload=generation_payload,
            prompt_hash=prompt_hash,
            status="queued",
            model_name=settings.OPENAI_TEXT_MODEL,
            include_image=validated_data.get("include_image", False),
        )
        UsageEventService().record_generation_usage(
            user=user,
            event_type="cache_miss",
            usage={},
            cache_hit=False,
        )

        from apps.generation.tasks import run_copy_generation_task

        transaction.on_commit(lambda: run_copy_generation_task.delay(str(job.id)))
        return SubmissionResult(job=job, created=True, deduplicated=False)

    def execute_text_generation(self, *, job: GenerationJob) -> dict[str, Any]:
        client = OpenAIClient()
        prompts = self._build_prompts(job)
        result = client.generate_structured_text(
            system_prompt=prompts["system"],
            user_prompt=prompts["user"],
            schema=GENERATION_RESPONSE_SCHEMA,
            model=job.model_name or settings.OPENAI_TEXT_MODEL,
        )
        self.validate_output(result.payload)
        self.cache_result(job.prompt_hash, result.payload)
        return {
            "output_payload": result.payload,
            "usage": result.usage,
            "provider_response_id": result.response_id,
        }

    def validate_output(self, payload: dict[str, Any]) -> None:
        try:
            validate(payload, GENERATION_RESPONSE_SCHEMA)
        except JSONSchemaValidationError as exc:
            raise OpenAIResponseValidationError(str(exc)) from exc

    def cache_result(self, prompt_hash: str, payload: dict[str, Any]) -> None:
        cache.set(
            self._cache_key(prompt_hash),
            payload,
            timeout=settings.CONTENT_CACHE_TTL_SECONDS,
        )

    def get_cached_result(self, prompt_hash: str) -> dict[str, Any] | None:
        return cache.get(self._cache_key(prompt_hash))

    def cache_job_status(self, job: GenerationJob) -> None:
        cache.set(
            f"job_status:{job.id}",
            {
                "status": job.status,
                "cache_hit": job.cache_hit,
                "updated_at": job.updated_at.isoformat(),
            },
            timeout=settings.JOB_STATUS_CACHE_TTL_SECONDS,
        )

    def _build_prompts(self, job: GenerationJob) -> dict[str, str]:
        brand = job.input_payload["brand_profile"]
        request = job.input_payload["request"]
        template_block = ""
        if job.input_payload.get("template"):
            template_block = f"Use this content template when helpful: {job.input_payload['template']['prompt_template']}\n"

        system_prompt = (
            "You are a senior marketing copywriter. "
            "Return only JSON that exactly matches the provided schema. "
            "Do not include reasoning or hidden deliberation. "
            "Avoid banned phrases and unsafe or deceptive claims."
        )
        user_prompt = (
            f"Brand name: {brand['brand_name']}\n"
            f"Brand voice: {brand['brand_voice']}\n"
            f"Preferred tone: {brand['preferred_tone']}\n"
            f"Target audience: {brand['target_audience']}\n"
            f"Product description: {brand['product_description']}\n"
            f"Example copy: {brand['example_copy']}\n"
            f"Banned phrases: {', '.join(brand['banned_phrases']) if brand['banned_phrases'] else 'None'}\n"
            f"{template_block}"
            f"Channel: {request['channel']}\n"
            f"Objective: {request['objective']}\n"
            f"Tone: {request['tone']}\n"
            f"Audience: {request['audience']}\n"
            f"Campaign product description: {request['product_description']}\n"
            f"Length: {request['length']}\n"
            f"CTA: {request['cta']}\n"
            f"Key points: {', '.join(request['key_points'])}\n"
            f"Output count: {request['output_count']}\n"
            "Return concise high-quality marketing variants with an image prompt that matches the campaign."
        )
        return {"system": system_prompt, "user": user_prompt}

    def _run_basic_safety_checks(self, validated_data: dict[str, Any]) -> None:
        banned = {"guaranteed profit", "fake review", "misleading claim"}
        text = " ".join(
            [
                validated_data.get("product_description", ""),
                " ".join(validated_data.get("key_points", [])),
                validated_data.get("cta", ""),
            ]
        ).lower()
        violations = [phrase for phrase in banned if phrase in text]
        if violations:
            raise ModerationError("Request contains disallowed marketing language.")

    def _cache_key(self, prompt_hash: str) -> str:
        return f"generation_result:{prompt_hash}"
