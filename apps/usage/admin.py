from django.contrib import admin

from .models import UsageEvent


@admin.register(UsageEvent)
class UsageEventAdmin(admin.ModelAdmin):
    list_display = ("user", "event_type", "tokens_in", "tokens_out", "latency_ms", "cache_hit", "created_at")
    list_filter = ("event_type", "cache_hit", "created_at")
    search_fields = ("user__email", "metadata")
    readonly_fields = ("created_at",)

