from django.contrib.admin import SimpleListFilter


class UserStatusFilter(SimpleListFilter):
    title = "Status"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            ("active", "Active"),
            ("inactive", "Inactive"),
        )

    def queryset(self, request, queryset):
        if self.value() == "inactive":
            return queryset.filter(is_active=False)

        return queryset.filter(is_active=True)