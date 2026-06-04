from django.contrib import admin

from apps.generation.models import Asset, GenerationJob


@admin.register(GenerationJob)
class GenerationJobAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "brand_profile", "status", "cache_hit", "created_at")
    list_filter = ("status", "cache_hit", "include_image", "created_at")
    search_fields = ("id", "prompt_hash", "user__email", "brand_profile__brand_name")
    readonly_fields = ("created_at", "updated_at", "completed_at")


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("id", "generation_job", "asset_type", "mime_type", "created_at")
    list_filter = ("asset_type", "mime_type", "created_at")
    search_fields = ("id", "generation_job__id", "storage_url")
