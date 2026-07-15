from django.contrib import admin


@admin.action(description="Deactivate selected users")
def deactivate_users(modeladmin, request, queryset):
    queryset.update(is_active=False)


@admin.action(description="Activate selected users")
def activate_users(modeladmin, request, queryset):
    queryset.update(is_active=True)