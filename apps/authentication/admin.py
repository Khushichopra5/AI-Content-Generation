from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import APIToken, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("-created_at",)
    list_display = ("email", "name", "role", "is_staff", "is_active", "created_at")
    list_filter = ("role", "is_staff", "is_active", "is_superuser")
    search_fields = ("email", "name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Profile", {"fields": ("name", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at", "last_login")
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "password1", "password2", "role", "is_staff", "is_active"),
            },
        ),
    )


@admin.register(APIToken)
class APITokenAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "prefix", "created_at", "last_used_at", "expires_at", "revoked_at")
    list_filter = ("revoked_at", "expires_at", "created_at")
    search_fields = ("user__email", "name", "prefix")
    readonly_fields = ("prefix", "key_digest", "created_at", "last_used_at", "revoked_at")

