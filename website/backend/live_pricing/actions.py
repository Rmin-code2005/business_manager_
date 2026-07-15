from django.contrib import admin


@admin.action(description="Soft Delete selected baskets")
def soft_delete_baskets(modeladmin, request, queryset):
    for basket in queryset:
        basket.delete()


@admin.action(description="Restore selected baskets")
def restore_baskets(modeladmin, request, queryset):
    for basket in queryset:
        basket.restore()


@admin.action(description="Hard Delete selected baskets")
def hard_delete_baskets(modeladmin, request, queryset):
    for basket in queryset:
        basket.hard_delete()