from django.contrib import admin

from apps.accounts.models import GuestUser


@admin.register(GuestUser)
class GuestUserAdmin(admin.ModelAdmin):
    list_display = ("id", "session_key", "restaurant", "created_at")
    list_filter = ("restaurant",)
    search_fields = ("session_key",)
    readonly_fields = ("created_at", "updated_at")
