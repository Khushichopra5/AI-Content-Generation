from __future__ import annotations

import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from apps.generation.models import Asset, GenerationJob
from apps.generation.services import GenerationService
from apps.generation.storage import get_storage_backend
from apps.integrations.openai_client import OpenAIClient, OpenAITransientError
from apps.usage.services import UsageEventService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(OpenAITransientError,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=5,
)
def run_copy_generation_task(self, job_id: str) -> None:
    job = GenerationJob.objects.select_related("user", "brand_profile", "template").get(id=job_id)
    if job.status == "succeeded":
        return

    service = GenerationService()
    job.status = "running"
    job.error_message = ""
    job.save(update_fields=["status", "error_message", "updated_at"])
    service.cache_job_status(job)

    try:
        result = service.execute_text_generation(job=job)
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        job.completed_at = timezone.now()
        job.save(update_fields=["status", "error_message", "completed_at", "updated_at"])
        service.cache_job_status(job)
        raise

    job.status = "succeeded"
    job.output_payload = result["output_payload"]
    job.completed_at = timezone.now()
    job.save(update_fields=["status", "output_payload", "completed_at", "updated_at"])
    service.cache_job_status(job)
    UsageEventService().record_generation_usage(
        user=job.user,
        event_type="generate_text",
        usage=result.get("usage", {}),
        cache_hit=job.cache_hit,
    )

    if job.include_image and job.output_payload.get("image_prompt"):
        transaction.on_commit(lambda: run_image_generation_task.delay(str(job.id)))


@shared_task(
    bind=True,
    autoretry_for=(OpenAITransientError,),
    retry_backoff=True,
    retry_backoff_max=300,
    retry_jitter=True,
    max_retries=5,
)
def run_image_generation_task(self, job_id: str) -> None:
    job = GenerationJob.objects.select_related("user").get(id=job_id)
    if job.assets.filter(asset_type="image").exists():
        return

    client = OpenAIClient()
    storage = get_storage_backend()
    result = client.generate_image(prompt=job.output_payload["image_prompt"])
    storage_url = storage.save_bytes(content=result.image_bytes, extension="png")
    Asset.objects.create(
        generation_job=job,
        asset_type="image",
        storage_url=storage_url,
        mime_type=result.mime_type,
        metadata={
            "revised_prompt": result.revised_prompt,
            "provider_response_id": result.response_id,
        },
    )
    UsageEventService().record_generation_usage(
        user=job.user,
        event_type="generate_image",
        usage={},
        cache_hit=False,
    )
