from django.contrib import admin

from .models import CustomUser
from .filters import UserStatusFilter
from .actions import (
    activate_users,
    deactivate_users,
)


@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "phone",
        "telegram_username",
        "active",
    )

    list_display_links = (
        "id",
        "email",
    )

    search_fields = (
        "email",
        "phone",
        "first_name",
        "last_name",
        "telegram_username",
    )

    ordering = (
        "-id",
    )

    list_filter = (
        UserStatusFilter,
    )

    actions = (
        deactivate_users,
        activate_users,
    )

    def get_queryset(self, request):
        # همه کاربران برگردانده می‌شوند تا امکان مشاهده و Restore وجود داشته باشد
        return self.model.objects.all()

    @admin.display(
        boolean=True,
        description="Active",
    )
    def active(self, obj):
        return obj.is_active