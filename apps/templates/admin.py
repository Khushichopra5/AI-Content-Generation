from django.contrib import admin

from .models import ContentTemplate


@admin.register(ContentTemplate)
class ContentTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "channel", "objective", "created_at")
    list_filter = ("channel", "objective", "created_at")
    search_fields = ("name", "user__email", "prompt_template")
    readonly_fields = ("created_at", "updated_at")

