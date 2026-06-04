from __future__ import annotations

import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from apps.authentication.models import APIToken, User
from apps.brands.models import BrandProfile
from apps.templates.models import ContentTemplate


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()


@pytest.fixture
def user(db) -> User:
    return User.objects.create_user(
        email="user@example.com",
        password="StrongPass123!",
        name="Test User",
    )


@pytest.fixture
def auth_token(user: User) -> str:
    return APIToken.issue_for_user(user, name="test").key


@pytest.fixture
def authenticated_client(api_client: APIClient, auth_token: str) -> APIClient:
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_token}")
    return api_client


@pytest.fixture
def brand_profile(user: User) -> BrandProfile:
    return BrandProfile.objects.create(
        user=user,
        brand_name="Acme",
        brand_voice="Confident and crisp",
        banned_phrases=["guaranteed profit"],
        preferred_tone="professional",
        example_copy="Ship faster with clear workflows.",
        product_description="AI workflow assistant",
        target_audience="startup operators",
    )


@pytest.fixture
def content_template(user: User) -> ContentTemplate:
    return ContentTemplate.objects.create(
        user=user,
        name="Launch Template",
        channel="social",
        objective="lead_generation",
        prompt_template="Focus on concise launch messaging.",
    )
