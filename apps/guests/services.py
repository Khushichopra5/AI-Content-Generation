from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.utils import timezone

from apps.authentication.models import User
from apps.brands.models import BrandProfile
from apps.generation.models import GenerationJob
from apps.guests.models import GuestSession, GuestSessionStatus
from apps.templates.models import ContentTemplate
from apps.usage.models import UsageEvent


@dataclass(slots=True)
class GuestLimitSummary:
    brands_used: int
    templates_used: int
    generations_used: int
    brands_soft_limit: int
    templates_soft_limit: int
    generations_soft_limit: int


class GuestSessionService:
    def bootstrap(
        self,
        *,
        guest_id: str | None = None,
        session_id: str | None = None,
        device_id: str | None = None,
    ) -> GuestSession:
        device_id = device_id or self._generate_prefixed_id("device")
        existing = None
        if guest_id and session_id:
            existing = self.resolve_session(
                guest_id=guest_id,
                session_id=session_id,
                device_id=device_id,
            )
        if existing:
            return existing

        guest_id = guest_id or self._generate_prefixed_id("guest")
        session_id = session_id or self._generate_prefixed_id("sess")
        with transaction.atomic():
            guest_user = User.objects.create_user(
                email=f"{guest_id}@guest.local",
                password=secrets.token_urlsafe(32),
                name="Guest User",
                is_guest=True,
            )
            guest_session = GuestSession.objects.create(
                guest_id=guest_id,
                session_id=session_id,
                device_id=device_id,
                backing_user=guest_user,
                expires_at=timezone.now() + timedelta(seconds=settings.GUEST_SESSION_TTL_SECONDS),
                metadata={"source": "bootstrap"},
            )
        self._cache_session(guest_session)
        return guest_session

    def resolve_session(self, *, guest_id: str, session_id: str, device_id: str) -> GuestSession | None:
        guest_session = (
            GuestSession.objects.select_related("backing_user")
            .filter(session_id=session_id, guest_id=guest_id, device_id=device_id)
            .first()
        )
        if not guest_session or not guest_session.is_active:
            if guest_session and guest_session.status == GuestSessionStatus.ACTIVE:
                guest_session.status = GuestSessionStatus.EXPIRED
                guest_session.save(update_fields=["status", "updated_at"])
            return None
        guest_session.touch(ttl_seconds=settings.GUEST_SESSION_TTL_SECONDS)
        self._cache_session(guest_session)
        return guest_session

    @transaction.atomic
    def migrate_guest_assets(self, *, guest_session: GuestSession, target_user: User) -> None:
        guest_user = guest_session.backing_user
        self._rehome_brand_profiles(guest_user=guest_user, target_user=target_user)
        self._rehome_templates(guest_user=guest_user, target_user=target_user)
        GenerationJob.objects.filter(user=guest_user).update(user=target_user)
        UsageEvent.objects.filter(user=guest_user).update(user=target_user)

        guest_session.claimed_by = target_user
        guest_session.status = GuestSessionStatus.CONVERTED
        guest_session.save(update_fields=["claimed_by", "status", "updated_at"])
        guest_user.is_active = False
        guest_user.save(update_fields=["is_active", "updated_at"])
        cache.delete(self._cache_key(guest_session.session_id))

    def summarize_limits(self, *, guest_session: GuestSession) -> GuestLimitSummary:
        start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        guest_user = guest_session.backing_user
        return GuestLimitSummary(
            brands_used=BrandProfile.objects.filter(user=guest_user, created_at__gte=start_of_day).count(),
            templates_used=ContentTemplate.objects.filter(user=guest_user, created_at__gte=start_of_day).count(),
            generations_used=GenerationJob.objects.filter(user=guest_user, created_at__gte=start_of_day).count(),
            brands_soft_limit=settings.GUEST_DAILY_BRAND_SOFT_LIMIT,
            templates_soft_limit=settings.GUEST_DAILY_TEMPLATE_SOFT_LIMIT,
            generations_soft_limit=settings.GUEST_DAILY_GENERATION_SOFT_LIMIT,
        )

    def _rehome_brand_profiles(self, *, guest_user: User, target_user: User) -> None:
        for brand in BrandProfile.objects.filter(user=guest_user).order_by("created_at"):
            base_name = brand.brand_name
            counter = 1
            while BrandProfile.objects.filter(user=target_user, brand_name=brand.brand_name).exists():
                counter += 1
                brand.brand_name = f"{base_name} ({counter})"
            brand.user = target_user
            brand.save(update_fields=["user", "brand_name", "updated_at"])

    def _rehome_templates(self, *, guest_user: User, target_user: User) -> None:
        for template in ContentTemplate.objects.filter(user=guest_user).order_by("created_at"):
            base_name = template.name
            counter = 1
            while ContentTemplate.objects.filter(user=target_user, name=template.name).exists():
                counter += 1
                template.name = f"{base_name} ({counter})"
            template.user = target_user
            template.save(update_fields=["user", "name", "updated_at"])

    def _cache_session(self, guest_session: GuestSession) -> None:
        cache.set(
            self._cache_key(guest_session.session_id),
            {
                "guest_id": guest_session.guest_id,
                "device_id": guest_session.device_id,
                "user_id": str(guest_session.backing_user_id),
            },
            timeout=settings.GUEST_SESSION_TTL_SECONDS,
        )

    def _cache_key(self, session_id: str) -> str:
        return f"{settings.GUEST_REDIS_KEY_PREFIX}:{session_id}"

    def _generate_prefixed_id(self, prefix: str) -> str:
        return f"{prefix}_{secrets.token_hex(4)}"
