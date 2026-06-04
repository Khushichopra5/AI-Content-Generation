from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.authentication.authentication import BearerTokenAuthentication
from apps.brands.models import BrandProfile
from apps.generation.models import GenerationJob
from apps.generation.serializers import (
    GenerationCreateSerializer,
    GenerationJobSerializer,
)
from apps.generation.services import GenerationService, ModerationError
from apps.templates.models import ContentTemplate


class GenerationJobViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = GenerationJobSerializer
    authentication_classes = [SessionAuthentication, BearerTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            GenerationJob.objects.filter(user=self.request.user)
            .select_related("brand_profile", "template")
            .prefetch_related("assets")
        )


class GenerationCreateView(APIView):
    authentication_classes = [SessionAuthentication, BearerTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return _submit_generation_request(request, include_image_override=None)


class ImageGenerationCreateView(APIView):
    authentication_classes = [SessionAuthentication, BearerTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return _submit_generation_request(request, include_image_override=True)


class RegenerateView(generics.GenericAPIView):
    authentication_classes = [SessionAuthentication, BearerTokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, job_id):
        original_job = get_object_or_404(
            GenerationJob.objects.filter(user=request.user).select_related("brand_profile", "template"),
            id=job_id,
        )
        payload = dict(original_job.input_payload["request"])
        payload["brand_profile_id"] = str(original_job.brand_profile_id)
        payload["template_id"] = str(original_job.template_id) if original_job.template_id else None
        payload["include_image"] = original_job.include_image
        serializer = GenerationCreateSerializer(
            data=payload,
            context={
                "brand_queryset": BrandProfile.objects.filter(user=request.user),
                "template_queryset": ContentTemplate.objects.filter(user=request.user),
            },
        )
        serializer.is_valid(raise_exception=True)
        service = GenerationService()
        result = service.submit_job(user=request.user, validated_data=serializer.validated_data)
        return Response(
            {
                "job_id": result.job.id,
                "status": result.job.status,
                "cache_hit": result.job.cache_hit,
                "deduplicated": result.deduplicated,
            },
            status=status.HTTP_201_CREATED if result.created else status.HTTP_200_OK,
        )


def _submit_generation_request(request, *, include_image_override):
    data = request.data.copy()
    if include_image_override is not None:
        data["include_image"] = include_image_override

    serializer = GenerationCreateSerializer(
        data=data,
        context={
            "brand_queryset": BrandProfile.objects.filter(user=request.user),
            "template_queryset": ContentTemplate.objects.filter(user=request.user),
        },
    )
    serializer.is_valid(raise_exception=True)
    service = GenerationService()
    try:
        result = service.submit_job(user=request.user, validated_data=serializer.validated_data)
    except ModerationError as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {
            "job_id": result.job.id,
            "status": result.job.status,
            "cache_hit": result.job.cache_hit,
            "deduplicated": result.deduplicated,
        },
        status=status.HTTP_201_CREATED if result.created else status.HTTP_200_OK,
    )
