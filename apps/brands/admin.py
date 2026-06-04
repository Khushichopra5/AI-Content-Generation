from django.contrib import admin

from .models import BrandProfile


@admin.register(BrandProfile)
class BrandProfileAdmin(admin.ModelAdmin):
    list_display = ("brand_name", "user", "preferred_tone", "created_at", "updated_at")
    list_filter = ("preferred_tone", "created_at", "updated_at")
    search_fields = ("brand_name", "user__email", "product_description", "target_audience")
    readonly_fields = ("created_at", "updated_at")

