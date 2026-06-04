from __future__ import annotations

import pytest

from apps.authentication.models import User
from apps.generation.models import Asset, GenerationJob
from apps.generation.tasks import run_copy_generation_task
from apps.integrations.openai_client import ImageGenerationResult, TextGenerationResult


@pytest.fixture
def immediate_on_commit(monkeypatch):
    monkeypatch.setattr("apps.generation.services.transaction.on_commit", lambda callback: callback())
    monkeypatch.setattr("apps.generation.tasks.transaction.on_commit", lambda callback: callback())


def build_generation_payload(brand_profile, content_template):
    return {
        "brand_profile_id": str(brand_profile.id),
        "template_id": str(content_template.id),
        "channel": "linkedin",
        "objective": "lead_generation",
        "tone": "professional",
        "audience": "startup founders",
        "product_description": "AI workflow assistant for go-to-market teams",
        "key_points": ["faster outreach", "better personalization"],
        "cta": "Book a demo",
        "output_count": 2,
        "include_image": True,
        "length": "medium",
    }


@pytest.mark.django_db
def test_brand_and_template_crud(authenticated_client):
    brand_response = authenticated_client.post(
        "/api/v1/brands/",
        {
            "brand_name": "Northwind",
            "brand_voice": "Warm and practical",
            "banned_phrases": ["best ever"],
            "preferred_tone": "friendly",
            "example_copy": "Stay in control without slowing down.",
            "product_description": "Planning software",
            "target_audience": "operations teams",
        },
        format="json",
    )
    assert brand_response.status_code == 201

    template_response = authenticated_client.post(
        "/api/v1/templates/",
        {
            "name": "Retention Email",
            "channel": "email",
            "objective": "retention",
            "prompt_template": "Write retention-focused lifecycle messaging.",
        },
        format="json",
    )
    assert template_response.status_code == 201

    brands_list = authenticated_client.get("/api/v1/brands/")
    templates_list = authenticated_client.get("/api/v1/templates/")

    assert brands_list.status_code == 200
    assert templates_list.status_code == 200
    assert brands_list.json()["count"] == 1
    assert templates_list.json()["count"] == 1


@pytest.mark.django_db
def test_generate_endpoint_queues_job_when_task_dispatch_is_stubbed(
    authenticated_client,
    brand_profile,
    content_template,
    monkeypatch,
    immediate_on_commit,
):
    dispatched = []

    monkeypatch.setattr(
        "apps.generation.tasks.run_copy_generation_task.delay",
        lambda job_id: dispatched.append(job_id),
    )

    response = authenticated_client.post(
        "/api/v1/generate/",
        build_generation_payload(brand_profile, content_template),
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["status"] == "queued"
    assert response.json()["cache_hit"] is False
    assert len(dispatched) == 1


@pytest.mark.django_db
def test_generation_task_persists_structured_output_and_asset(
    authenticated_client,
    user: User,
    brand_profile,
    content_template,
    monkeypatch,
    immediate_on_commit,
):
    monkeypatch.setattr(
        "apps.integrations.openai_client.OpenAIClient.generate_structured_text",
        lambda self, **kwargs: TextGenerationResult(
            payload={
                "variants": [
                    {
                        "variant_id": "v1",
                        "headline": "Launch faster",
                        "body": "Move from brief to campaign in minutes.",
                        "cta": "Book a demo",
                        "tone_score": 0.94,
                    }
                ],
                "hashtags": ["#ai", "#marketing"],
                "subject_lines": ["Launch faster with AI"],
                "cta_options": ["Book a demo"],
                "image_prompt": "Minimal SaaS marketing hero image",
                "quality_notes": ["Aligned with brand voice"],
            },
            usage={"input_tokens": 50, "output_tokens": 75},
            response_id="resp_text_123",
        ),
    )
    monkeypatch.setattr(
        "apps.integrations.openai_client.OpenAIClient.generate_image",
        lambda self, **kwargs: ImageGenerationResult(
            image_bytes=b"fake-image-bytes",
            mime_type="image/png",
            revised_prompt="Minimal SaaS marketing hero image",
            response_id="resp_img_123",
        ),
    )

    response = authenticated_client.post(
        "/api/v1/generate/",
        build_generation_payload(brand_profile, content_template),
        format="json",
    )
    assert response.status_code == 201

    job = GenerationJob.objects.get(id=response.json()["job_id"])
    run_copy_generation_task(str(job.id))
    job.refresh_from_db()

    assert job.status == "succeeded"
    assert job.output_payload["variants"][0]["headline"] == "Launch faster"
    assert job.assets.count() == 1
    asset = job.assets.get()
    assert asset.asset_type == "image"
    assert Asset.objects.count() == 1


@pytest.mark.django_db
def test_cached_repeat_request_returns_succeeded_without_second_model_call(
    authenticated_client,
    brand_profile,
    content_template,
    monkeypatch,
    immediate_on_commit,
):
    calls = {"text": 0, "image": 0}

    def fake_text(self, **kwargs):
        calls["text"] += 1
        return TextGenerationResult(
            payload={
                "variants": [
                    {
                        "variant_id": "v1",
                        "headline": "Cache headline",
                        "body": "Cached body",
                        "cta": "Book a demo",
                        "tone_score": 0.91,
                    }
                ],
                "hashtags": ["#cache"],
                "subject_lines": ["Cached subject"],
                "cta_options": ["Book a demo"],
                "image_prompt": "Cache image prompt",
                "quality_notes": ["Cached note"],
            },
            usage={"input_tokens": 10, "output_tokens": 20},
            response_id="resp_cache_1",
        )

    def fake_image(self, **kwargs):
        calls["image"] += 1
        return ImageGenerationResult(
            image_bytes=b"img",
            mime_type="image/png",
            revised_prompt="Cache image prompt",
            response_id="resp_cache_img",
        )

    monkeypatch.setattr("apps.integrations.openai_client.OpenAIClient.generate_structured_text", fake_text)
    monkeypatch.setattr("apps.integrations.openai_client.OpenAIClient.generate_image", fake_image)

    payload = build_generation_payload(brand_profile, content_template)
    first = authenticated_client.post("/api/v1/generate/", payload, format="json")
    assert first.status_code == 201

    second = authenticated_client.post("/api/v1/generate/", payload, format="json")
    assert second.status_code == 201
    assert second.json()["cache_hit"] is True

    assert calls["text"] == 1
    assert calls["image"] == 1


@pytest.mark.django_db
def test_usage_endpoint_returns_generation_events(
    authenticated_client,
    brand_profile,
    content_template,
    monkeypatch,
    immediate_on_commit,
):
    monkeypatch.setattr(
        "apps.integrations.openai_client.OpenAIClient.generate_structured_text",
        lambda self, **kwargs: TextGenerationResult(
            payload={
                "variants": [
                    {
                        "variant_id": "v1",
                        "headline": "Usage headline",
                        "body": "Usage body",
                        "cta": "Try it",
                        "tone_score": 0.9,
                    }
                ],
                "hashtags": ["#usage"],
                "subject_lines": ["Usage subject"],
                "cta_options": ["Try it"],
                "image_prompt": "",
                "quality_notes": ["Usage note"],
            },
            usage={"input_tokens": 5, "output_tokens": 7},
            response_id="resp_usage",
        ),
    )

    payload = build_generation_payload(brand_profile, content_template)
    payload["include_image"] = False
    authenticated_client.post("/api/v1/generate/", payload, format="json")

    usage_response = authenticated_client.get("/api/v1/usage/")
    assert usage_response.status_code == 200
    assert usage_response.json()["count"] >= 2
