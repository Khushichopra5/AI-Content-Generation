from __future__ import annotations

import pytest

from apps.brands.models import BrandProfile
from apps.generation.models import GenerationJob
from apps.templates.models import ContentTemplate


def _guest_generation_payload(brand_profile: BrandProfile, template: ContentTemplate) -> dict:
    return {
        "brand_profile_id": str(brand_profile.id),
        "template_id": str(template.id),
        "channel": "linkedin",
        "objective": "product_launch",
        "tone": "confident",
        "audience": "recruiters and developers",
        "product_description": "Guest-first AI marketing content playground",
        "key_points": ["guest mode", "content generation", "observability"],
        "cta": "Try the demo",
        "output_count": 1,
        "include_image": False,
        "length": "short",
    }


@pytest.fixture
def immediate_on_commit(monkeypatch):
    monkeypatch.setattr("apps.generation.services.transaction.on_commit", lambda callback: callback())
    monkeypatch.setattr("apps.generation.tasks.transaction.on_commit", lambda callback: callback())


@pytest.mark.django_db
def test_guest_bootstrap_creates_persistent_guest_identity(api_client, guest_session):
    response = api_client.post(
        "/api/v1/guest/bootstrap/",
        {
            "guest_id": guest_session.guest_id,
            "session_id": guest_session.session_id,
            "device_id": guest_session.device_id,
        },
        format="json",
    )

    assert response.status_code == 201
    assert response.json()["session"]["guest_id"] == guest_session.guest_id
    assert response.json()["limits"]["generations_soft_limit"] > 0


@pytest.mark.django_db
def test_guest_can_create_resources_and_queue_generation(
    guest_client,
    immediate_on_commit,
    monkeypatch,
):
    dispatched: list[str] = []
    monkeypatch.setattr(
        "apps.generation.tasks.run_copy_generation_task.delay",
        lambda job_id: dispatched.append(job_id),
    )

    brand_response = guest_client.post(
        "/api/v1/brands/",
        {
            "brand_name": "Guest Brand",
            "brand_voice": "Direct and helpful",
            "banned_phrases": ["guaranteed profit"],
            "preferred_tone": "clear",
            "example_copy": "Ship real demos quickly.",
            "product_description": "Anonymous AI marketing demo",
            "target_audience": "recruiters",
        },
        format="json",
    )
    assert brand_response.status_code == 201

    template_response = guest_client.post(
        "/api/v1/templates/",
        {
            "name": "Guest Launch Template",
            "channel": "social",
            "objective": "product_launch",
            "prompt_template": "Focus on demoability and clarity.",
        },
        format="json",
    )
    assert template_response.status_code == 201

    generation_response = guest_client.post(
        "/api/v1/generate/",
        _guest_generation_payload(
            BrandProfile.objects.get(id=brand_response.json()["id"]),
            ContentTemplate.objects.get(id=template_response.json()["id"]),
        ),
        format="json",
    )
    assert generation_response.status_code == 201
    assert generation_response.json()["status"] == "queued"
    assert len(dispatched) == 1


@pytest.mark.django_db
def test_guest_registration_migrates_guest_owned_data(
    guest_client,
    guest_session,
):
    brand_response = guest_client.post(
        "/api/v1/brands/",
        {
            "brand_name": "Guest Import Brand",
            "brand_voice": "Curious",
            "banned_phrases": [],
            "preferred_tone": "friendly",
            "example_copy": "Try before you sign up.",
            "product_description": "Guest migration demo",
            "target_audience": "hiring teams",
        },
        format="json",
    )
    assert brand_response.status_code == 201

    register_response = guest_client.post(
        "/api/v1/auth/register/",
        {
            "email": "guest-migrate@example.com",
            "name": "Migrated Guest",
            "password": "StrongPass123!",
        },
        format="json",
    )
    assert register_response.status_code == 201
    registered_user = register_response.json()["user"]

    imported_brand = BrandProfile.objects.get(id=brand_response.json()["id"])
    imported_brand.refresh_from_db()
    assert str(imported_brand.user_id) == registered_user["id"]

    guest_session.refresh_from_db()
    assert guest_session.status == "converted"
    assert str(guest_session.claimed_by_id) == registered_user["id"]
